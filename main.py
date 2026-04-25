import streamlit as st
import os, json, base64
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(layout="wide", page_title="報告檢索系統")

# 定義絕對路徑
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(CUR_DIR, "reports")
HTML_FILE = os.path.join(CUR_DIR, "test.html")

def get_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def load_data():
    if not os.path.exists(PDF_DIR):
        print(f"錯誤: 找不到目錄 {PDF_DIR}")
        return []
    
    files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    print(f"--- 正在掃描 reports 資料夾，發現 {len(files)} 個檔案 ---")
    
    results = []
    for f in files:
        f_path = os.path.join(PDF_DIR, f)
        print(f"正在處理: {f}")
        info = extract_financial_data(f_path)
        info["pdfData"] = f"data:application/pdf;base64,{get_b64(f_path)}"
        info["filename"] = f
        results.append(info)
    return results

st.title("券商研究報告檢索系統")

if not os.path.exists(HTML_FILE):
    st.error(f"找不到 test.html，請確認它在: {HTML_FILE}")
else:
    # 載入資料
    all_data = load_data()
    
    # 讀取模板
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_template = f.read()
    
    # 關鍵：將 Python 資料轉為 JSON 注入 HTML
    json_payload = json.dumps(all_data, ensure_ascii=False)
    # 替換 HTML 內的預留變數
    rendered_html = html_template.replace("const src = [];", f"const src = {json_payload};")
    
    # 輸出到 Streamlit
    components.html(rendered_html, height=1200, scrolling=True)
    
    # 同步在 Streamlit 頁面顯示 debug 訊息 (確認 Python 有抓到資料)
    if not all_data:
        st.warning("Python 端目前抓到的資料清單是空的，請檢查 reports 資料夾。")
