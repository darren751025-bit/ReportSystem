import streamlit as st
import os
import json
import base64
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(page_title="券商報告檢索", layout="wide")

# 強制指向執行檔所在的資料夾
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
HTML_FILE = os.path.join(BASE_DIR, "test.html")

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def load_reports():
    if not os.path.exists(REPORT_DIR):
        st.error(f"❌ 找不到 reports 資料夾！預期位置：{REPORT_DIR}")
        return []
    
    pdf_files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    results = []
    
    for f in pdf_files:
        full_path = os.path.join(REPORT_DIR, f)
        info = extract_financial_data(full_path)
        # 轉換成網頁可讀取的 Base64
        info["pdfData"] = f"data:application/pdf;base64,{get_base64(full_path)}"
        info["filename"] = f
        results.append(info)
    return results

st.title("📂 證券研究報告系統")

# 檢查 HTML 是否存在
if not os.path.exists(HTML_FILE):
    st.error(f"❌ 找不到 test.html！預期位置：{HTML_FILE}")
else:
    reports = load_reports()
    
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 注入資料
    json_data = json.dumps(reports, ensure_ascii=False)
    final_html = html_content.replace("const src = [];", f"const src = {json_data};")
    
    # 顯示元件
    components.html(final_html, height=900, scrolling=True)
