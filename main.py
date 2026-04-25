import streamlit as st
import pandas as pd
import os
import json
import base64
from datetime import datetime, date
import streamlit.components.v1 as components
from parsers import extract_financial_data

# --- 1. 配置與路徑 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")
HTML_TEMPLATE = os.path.join(BASE_DIR, "test.html")

st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

# --- 2. 核心邏輯：自動同步與解析 PDF ---
def sync_reports():
    if os.path.exists(CACHE_CSV):
        df = pd.read_csv(CACHE_CSV)
    else:
        df = pd.DataFrame(columns=["date", "code", "name", "broker", "rec", "target", "last", "filename"])

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_data = []
    
    # 檢查是否有新檔案
    existing_files = df['filename'].tolist() if not df.empty else []
    for pdf in all_pdfs:
        if pdf not in existing_files:
            info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
            # 轉換為 HTML 版面需要的欄位格式
            new_data.append({
                "date": info.get("日期", datetime.now().strftime("%m.%d")),
                "code": info.get("代號", ""),
                "name": info.get("名稱", ""),
                "broker": info.get("券商", ""),
                "rec": info.get("建議", ""),
                "target": info.get("目標價", ""),
                "last": info.get("昨收", ""),
                "filename": pdf
            })
    
    if new_data:
        df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
        df.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    return df

# --- 3. 登入檢查 ---
def check_login(u, p):
    if not os.path.exists(USER_DB): return False
    try:
        users = pd.read_csv(USER_DB)
        match = users[(users['account'].astype(str) == str(u)) & (users['password'].astype(str) == str(p))]
        if not match.empty:
            expiry = datetime.strptime(str(match.iloc[0]['expiry_date']), "%Y-%m-%d").date()
            if date.today() <= expiry: return True, ""
            return False, f"❌ 帳號已於 {expiry} 過期，請聯繫管理員。"
        return False, "❌ 帳號或密碼錯誤。"
    except: return False, "系統錯誤"

# --- 4. 渲染 HTML 版面 ---
def render_custom_html(df):
    if not os.path.exists(HTML_TEMPLATE):
        st.error("找不到 test.html 檔案")
        return

    # 將數據轉為 JSON 供 JavaScript 使用
    report_json = df.to_json(orient='records', force_ascii=False)
    
    with open(HTML_TEMPLATE, "r", encoding="utf-8") as f:
        html_code = f.read()

    # 關鍵：將 HTML 內的靜態數據替換為動態 JSON
    # 假設你的 test.html 裡有一行是 const src = [...];
    # 我們將其替換為 Python 產生的資料
    dynamic_html = html_code.replace(
        "const src = [];", f"const src = {report_json};"
    ).replace(
        "let src = [];", f"let src = {report_json};"
    )
    
    # 渲染組件 (高度根據內容調整)
    components.html(dynamic_html, height=900, scrolling=True)

# --- 5. 主程式流程 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 系統登入")
    with st.container():
        u = st.text_input("帳號")
        p = st.text_input("密碼", type="password")
        if st.button("登入", use_container_width=True):
            success, msg = check_login(u, p)
            if success:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error(msg)
else:
    # 1. 先抓取最新資料
    df_reports = sync_reports()
    
    # 2. 顯示你想要的 HTML 版面
    render_custom_html(df_reports)
    
    # 3. 側邊欄輔助功能
    with st.sidebar:
        st.success("會員登入中")
        if st.button("登出"):
            st.session_state.auth = False
            st.rerun()
