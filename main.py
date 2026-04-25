import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date
import streamlit.components.v1 as components
from parsers import extract_financial_data

# --- 1. 配置與路徑 ---
st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")
HTML_FILE = os.path.join(BASE_DIR, "test.html")

# 確保目錄存在
for path in [PDF_FOLDER, os.path.dirname(CACHE_CSV)]:
    if not os.path.exists(path):
        os.makedirs(path)

# --- 2. 解析邏輯 ---
def sync_data():
    cols = ["date", "code", "name", "broker", "rec", "target", "last", "filename"]
    df_cache = pd.DataFrame(columns=cols)
    
    if os.path.exists(CACHE_CSV):
        try:
            df_cache = pd.read_csv(CACHE_CSV)
            if 'filename' not in df_cache.columns:
                df_cache = pd.DataFrame(columns=cols)
        except:
            pass

    if not os.path.exists(PDF_FOLDER):
        st.error(f"找不到夾路徑: {PDF_FOLDER}")
        return df_cache

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    
    if not all_pdfs:
        st.warning(f"⚠️ 警告：在 {PDF_FOLDER} 資料夾中沒看到任何 PDF 檔案！")
    
    existing_files = df_cache['filename'].tolist() if not df_cache.empty else []
    new_entries = []
    
    for pdf in all_pdfs:
        if pdf not in existing_files:
            try:
                info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
                entry = {
                    "date": info.get("日期", datetime.now().strftime("%m.%d")),
                    "code": info.get("代號", ""),
                    "name": info.get("名稱", ""),
                    "broker": info.get("券商", ""),
                    "rec": info.get("建議", ""),
                    "target": str(info.get("目標價", "")),
                    "last": str(info.get("昨收", "")),
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

# --- 3. 登入邏輯 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業報告系統")
    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")
    if st.button("登入", use_container_width=True):
        if os.path.exists(USER_DB):
            users = pd.read_csv(USER_DB)
            match = users[(users['account'].astype(str)==u) & (users['password'].astype(str)==p)]
            if not match.empty:
                st.session_state.auth = True
                st.rerun()
            else: st.error("帳密錯誤")
        else: st.error("找不到帳號資料檔")
else:
    # 執行同步
    df = sync_data()
    
    # 讀取 HTML
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 轉換資料
        json_data = df.to_json(orient='records', force_ascii=False)
        
        # 強制替換 (考慮到 test.html 裡可能有 let 或 const)
        final_html = html_content.replace("let src = [];", f"const src = {json_data};")
        final_html = final_html.replace("const src = [];", f"const src = {json_data};")
        
        # 渲染
        components.html(final_html, height=1200, scrolling=True)
    else:
        st.error("找不到 test.html 檔案")

    with st.sidebar:
        if st.button("登出"):
            st.session_state.auth = False
            st.rerun()
