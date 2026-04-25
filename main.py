import streamlit as st
import json
import os
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(layout="wide")

def load_and_inject_data():
    REPORT_DIR = "reports"
    all_reports = []
    
    # 1. 掃描 PDF 並解析
    if os.path.exists(REPORT_DIR):
        files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
        for f in files:
            data = extract_financial_data(os.path.join(REPORT_DIR, f))
            # 補上 URL 供 HTML 下載使用
            data['url'] = f"reports/{f}"
            all_reports.append(data)
            
    # 2. 轉成 JSON
    json_str = json.dumps(all_reports, ensure_ascii=False)
    
    # 3. 讀取並替換 HTML 內容
    with open("test.html", "r", encoding="utf-8") as f:
        html_template = f.read()
    
    # 精準替換
    final_html = html_template.replace("[/* DATA_PLACEHOLDER */]", json_str)
    return final_html

try:
    final_content = load_and_inject_data()
    # 渲染畫面，高度設為 1000 以確保圖表顯示完整
    components.html(final_content, height=1000, scrolling=True)
except Exception as e:
    st.error(f"系統錯誤：{e}")
