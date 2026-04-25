import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")
HTML_FILE = os.path.join(BASE_DIR, "test.html")

# 確保目錄存在
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(CACHE_CSV), exist_ok=True)

# --- 1. 自動偵測與解析邏輯 ---
def sync_data():
    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    
    def normalize_info(info, filename):
        # 這裡處理 parsers.py 回傳的中英文 Key 轉換
        return {
            "date": str(info.get("日期") or info.get("date") or datetime.now().strftime("%m.%d")),
            "code": str(info.get("代號") or info.get("code") or ""),
            "name": str(info.get("名稱") or info.get("name") or ""),
            "broker": str(info.get("券商") or info.get("broker") or ""),
            "rec": str(info.get("建議") or info.get("rec") or "未分類"),
            "target": str(info.get("目標價") or info.get("target") or ""),
            "last": str(info.get("昨收") or info.get("last") or ""),
            "filename": filename
        }

    if not all_pdfs:
        return pd.DataFrame()

    results = []
    for pdf in all_pdfs:
        try:
            path = os.path.join(PDF_FOLDER, pdf)
            raw_info = extract_financial_data(path)
            clean_info = normalize_info(raw_info, pdf)
            results.append(clean_info)
        except Exception as e:
            st.error(f"解析檔案 {pdf} 出錯: {e}")

    df = pd.DataFrame(results)
    if not df.empty:
        df.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    return df

# --- 2. 登入系統 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業報告檢索系統")
    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")
    if st.button("登入", use_container_width=True):
        if os.path.exists(USER_DB):
            users = pd.read_csv(USER_DB)
            if any((users['account'].astype(str) == u) & (users['password'].astype(str) == p)):
                st.session_state.auth = True
                st.rerun()
            else: st.error("帳密錯誤")
        else: st.error("系統檔案缺失 (Member account.csv)")
else:
    # 登入成功：抓取數據
    df_data = sync_data()
    
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            tmpl = f.read()
        
        # 準備 JSON 字串
        if df_data.empty:
            final_json = "[]"
        else:
            final_json = df_data.to_json(orient='records', force_ascii=False)
        
        # --- 核心修復：統一替換邏輯 ---
        # 尋找 test.html 中的 const src = []; 並替換成真正的 JSON
        output_html = tmpl.replace("const src = [];", f"const src = {final_json};")
        output_html = output_html.replace("let src = [];", f"const src = {final_json};")
        
        # 渲染 HTML
        components.html(output_html, height=1000, scrolling=True)
    else:
        st.error(f"找不到 HTML 檔案: {HTML_FILE}")

    with st.sidebar:
        if st.button("登出"):
            st.session_state.auth = False
            st.rerun()
