import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import streamlit.components.v1 as components
from parsers import extract_financial_data

# --- 基礎配置 ---
st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
HTML_FILE = os.path.join(BASE_DIR, "test.html")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")

# 確保必要的資料夾存在
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(CACHE_CSV), exist_ok=True)

def get_all_reports():
    """掃描 reports 資料夾並透過 parsers.py 解析 PDF"""
    if not os.path.exists(PDF_FOLDER):
        return []
    
    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    results = []
    
    for pdf in all_pdfs:
        try:
            path = os.path.join(PDF_FOLDER, pdf)
            # 呼叫你的解析器
            info = extract_financial_data(path)
            
            # 標準化欄位名稱，確保與 test.html 中的 JS 對應
            report_item = {
                "date": str(info.get("日期") or info.get("date") or datetime.now().strftime("%m.%d")),
                "code": str(info.get("代號") or info.get("code") or ""),
                "name": str(info.get("名稱") or info.get("name") or ""),
                "broker": str(info.get("券商") or info.get("broker") or ""),
                "rec": str(info.get("建議") or info.get("rec") or "中立"),
                "target": str(info.get("目標價") or info.get("target") or "-"),
                "last": str(info.get("昨收") or info.get("last") or "-"),
                "filename": pdf
            }
            results.append(report_item)
        except Exception as e:
            print(f"解析 {pdf} 失敗: {e}")
            continue
            
    return results

# --- 登入邏輯 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業報告檢索系統")
    col1, col2 = st.columns(2)
    with col1:
        u = st.text_input("帳號")
        p = st.text_input("密碼", type="password")
        if st.button("登入系統", use_container_width=True):
            if os.path.exists(USER_DB):
                users = pd.read_csv(USER_DB)
                if any((users['account'].astype(str)==u) & (users['password'].astype(str)==p)):
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("帳號或密碼錯誤")
            else: st.error("系統檔案缺失 (Member account.csv)")
else:
    # --- 登入後主畫面 ---
    with st.spinner("正在加載最新報告..."):
        reports_data = get_all_reports()
    
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html_template = f.read()
        
        # 將 Python 列表轉為 JSON 字串
        json_data_str = json.dumps(reports_data, ensure_ascii=False)
        
        # 關鍵注入點：替換 test.html 裡的變數
        final_html = html_template.replace("const src = [];", f"const src = {json_data_str};")
        
        # 顯示 HTML 組件
        components.html(final_html, height=1200, scrolling=True)
    else:
        st.error("找不到 test.html 檔案，請確認檔案位置。")

    with st.sidebar:
        st.write(f"當前用戶: 管理員")
        if st.button("登出"):
            st.session_state.auth = False
            st.rerun()
