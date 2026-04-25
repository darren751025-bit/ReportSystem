import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 強制檢查目錄名稱，防止大小寫問題
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
HTML_FILE = os.path.join(BASE_DIR, "test.html")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")

os.makedirs(PDF_FOLDER, exist_ok=True)

def get_report_data():
    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    if not all_pdfs:
        return []

    results = []
    for pdf in all_pdfs:
        try:
            path = os.path.join(PDF_FOLDER, pdf)
            # 取得解析數據
            info = extract_financial_data(path)
            # 統一欄位名稱給前端 JS 使用
            results.append({
                "date": str(info.get("日期", info.get("date", "01.01"))),
                "code": str(info.get("代號", info.get("code", ""))),
                "name": str(info.get("名稱", info.get("name", ""))),
                "broker": str(info.get("券商", info.get("broker", ""))),
                "rec": str(info.get("建議", info.get("rec", "未分類"))),
                "target": str(info.get("目標價", info.get("target", ""))),
                "last": str(info.get("昨收", info.get("last", ""))),
                "filename": pdf
            })
        except:
            continue
    return results

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業報告系統")
    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")
    if st.button("進入系統"):
        if os.path.exists(USER_DB):
            users = pd.read_csv(USER_DB)
            if any((users['account'].astype(str)==u) & (users['password'].astype(str)==p)):
                st.session_state.auth = True
                st.rerun()
            else: st.error("帳密錯誤")
        else: st.error("缺少會員資料檔")
else:
    # 核心邏輯
    data_list = get_report_data()
    
    # 偵錯用：如果你在網頁上看到 []，代表 PDF 解析失敗
    # st.write(f"偵測到的資料量: {len(data_list)}") 

    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            tmpl = f.read()
        
        json_str = json.dumps(data_list, ensure_ascii=False)
        
        # 精準替換
        final_html = tmpl.replace("const src = [];", f"const src = {json_str};")
        
        components.html(final_html, height=1000, scrolling=True)
    else:
        st.error("缺少 test.html")
