import streamlit as st
import pandas as pd
import os
import json
import base64
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(page_title="券商報告檢索系統", layout="wide")

REPORT_DIR = "reports"  # PDF 存放資料夾

def get_pdf_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def load_all_reports():
    if not os.path.exists(REPORT_DIR): return []
    files = [f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")]
    results = []
    for f in files:
        path = os.path.join(REPORT_DIR, f)
        info = extract_financial_data(path)
        # 注入 PDF Base64 數據以便預覽
        info["pdfData"] = f"data:application/pdf;base64,{get_pdf_base64(path)}"
        info["filename"] = f
        results.append(info)
    return results

st.title("📂 專業券商報告檢索系統")

# 模擬登入 (可依需求保留或移除)
if 'login' not in st.session_state: st.session_state.login = True 

if st.session_state.login:
    data_list = load_all_reports()
    
    # 讀取 HTML 模板
    with open("test.html", "r", encoding="utf-8") as f:
        html_template = f.read()
    
    # 將資料注入 HTML
    json_data = json.dumps(data_list, ensure_ascii=False)
    final_html = html_template.replace("const src = [];", f"const src = {json_data};")
    
    components.html(final_html, height=1000, scrolling=True)
