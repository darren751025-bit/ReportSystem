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

# --- 1. 自動偵測與解析邏輯 ---
def sync_data():
    # 強制檢查 reports 資料夾
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        return pd.DataFrame()

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    
    # 定義標準化的欄位 (為了對接 HTML)
    def normalize_info(info, filename):
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

    # 如果沒有 PDF，直接回傳空資料
    if not all_pdfs:
        return pd.DataFrame()

    results = []
    for pdf in all_pdfs:
        try:
            path = os.path.join(PDF_FOLDER, pdf)
            # 呼叫解析引擎
            raw_info = extract_financial_data(path)
            # 進行中英文 Key 轉換與標準化
            clean_info = normalize_info(raw_info, pdf)
            results.append(clean_info)
        except Exception as e:
            st.error(f"解析檔案 {pdf} 出錯: {e}")

    df = pd.DataFrame(results)
    # 存檔供備份
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
    # 登入成功
    df_data = sync_data()
    
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            tmpl = f.read()
        
        # 準備注入的 JSON
        if df_data.empty:
            json_str = "[]"
        else:
            json_str = df_data.to_json(orient='records', force_ascii=False)
        
        # 強力替換：無論你 HTML 寫 let 還是 const
        final_html = tmpl.replace("let src = [];", f"const src = {json_data};") # 防呆
        final_html = tmpl.replace("const src = [];", f"const src = {json_str};")
        
        components.html(final_html, height=1000, scrolling=True)
    else:
        st.error("找不到 test.html 檔案")

    with st.sidebar:
        if st.button("登出"):
            st.session_state.auth = False
            st.rerun()
