import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date
import streamlit.components.v1 as components
from parsers import extract_financial_data

# --- 1. 基礎配置與路徑 ---
st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")
HTML_FILE = os.path.join(BASE_DIR, "test.html")

# 確保必要目錄存在
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(CACHE_CSV), exist_ok=True)

# --- 2. 核心功能：同步與解析 PDF ---
def sync_data():
    if os.path.exists(CACHE_CSV):
        try:
            df_cache = pd.read_csv(CACHE_CSV)
        except:
            df_cache = pd.DataFrame(columns=["date", "code", "name", "broker", "rec", "target", "last", "filename"])
    else:
        df_cache = pd.DataFrame(columns=["date", "code", "name", "broker", "rec", "target", "last", "filename"])

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_entries = []

    # 找出尚未解析過的檔案
    existing_files = df_cache['filename'].tolist() if not df_cache.empty else []
    
    for pdf in all_pdfs:
        if pdf not in existing_files:
            with st.spinner(f'解析新報告中: {pdf}...'):
                try:
                    # 呼叫 parsers.py 的解析引擎
                    info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
                    
                    # 格式化成 HTML 需要的 Key 名稱
                    entry = {
                        "date": info.get("日期", datetime.now().strftime("%m.%d")),
                        "code": info.get("代號", ""),
                        "name": info.get("名稱", ""),
                        "broker": info.get("券商", ""),
                        "rec": info.get("建議", ""),
                        "target": info.get("目標價", ""),
                        "last": info.get("昨收", ""),
                        "filename": pdf
                    }
                    new_entries.append(entry)
                except Exception as e:
                    st.error(f"解析 {pdf} 失敗: {e}")
    
    if new_entries:
        df_new = pd.DataFrame(new_entries)
        df_cache = pd.concat([df_cache, df_new], ignore_index=True)
        df_cache.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    
    return df_cache

# --- 3. 會員驗證與日期檢查 ---
def check_login(username, password):
    if not os.path.exists(USER_DB):
        st.error("找不到會員資料檔 (Member account.csv)")
        return False, ""
    
    try:
        users_df = pd.read_csv(USER_DB)
        match = users_df[(users_df['account'].astype(str) == str(username)) & 
                         (users_df['password'].astype(str) == str(password))]
        
        if not match.empty:
            expiry_str = str(match.iloc[0]['expiry_date']).strip()
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            
            if date.today() <= expiry_date:
                return True, "" # 通過
            else:
                return False, f"❌ 帳號已於 {expiry_str} 到期，請聯繫管理員。"
        return False, "❌ 帳號或密碼錯誤。"
    except Exception as e:
        return False, f"系統錯誤: {e}"

# --- 4. 介面控制流程 ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # 登入介面
    st.title("🛡️ 專業報告系統登入")
    with st.container():
        u = st.text_input("會員帳號")
        p = st.text_input("登入密碼", type="password")
        if st.button("確認進入系統", use_container_width=True):
            success, message = check_login(u, p)
            if success:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(message)
else:
    # 登入成功：處理數據並顯示 HTML
    df = sync_data()
    
    # 讀取你的 test.html 並注入資料
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 將 DataFrame 轉為 JSON 陣列
        json_data = df.to_json(orient='records', force_ascii=False)
        
        # 關鍵：將 HTML 裡的靜態變數替換為動態數據
        # 這樣 test.html 裡的所有 JS 功能（搜尋、排序、圖表）都能正常運作
        final_html = html_content.replace("const src = [];", f"const src = {json_data};")
        
        # 渲染組件
        components.html(final_html, height=1000, scrolling=True)
        
        # 側邊欄增加登出功能
        with st.sidebar:
            st.info(f"會員狀態：使用中")
            if st.button("安全登出"):
                st.session_state.authenticated = False
                st.rerun()
                
    except Exception as e:
        st.error(f"載入 HTML 範本失敗: {e}")
