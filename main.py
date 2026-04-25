import streamlit as st
import os, json, base64
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(layout="wide")

# 路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
HTML_FILE = os.path.join(BASE_DIR, "test.html")

# 1. 掃描檔案 (只抓文字資訊，不抓 PDF 二進制資料)
def load_meta_data():
    if not os.path.exists(REPORT_DIR): return []
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    results = []
    for f in files:
        f_path = os.path.join(REPORT_DIR, f)
        info = extract_financial_data(f_path) # 呼叫你的解析器
        info["filename"] = f
        results.append(info)
    return results

st.title("📊 券商報告檢索系統 (穩定版)")

# 載入基礎資料
meta_data = load_meta_data()

# 2. 處理 PDF 讀取請求 (這是在後台跑的，不會卡住網頁)
def get_pdf_b64(filename):
    target = os.path.join(REPORT_DIR, filename)
    with open(target, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 使用 Streamlit Sidebar 當作「預覽緩衝」
if "view_pdf" in st.session_state:
    st.sidebar.subheader(f"正在預覽: {st.session_state.view_file}")
    pdf_b64 = get_pdf_b64(st.session_state.view_file)
    pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_b64}" width="100%" height="800"></iframe>'
    st.sidebar.markdown(pdf_display, unsafe_allow_html=True)

# 3. 渲染網頁
if os.path.exists(HTML_FILE):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_code = f.read()
    
    # 只注入文字資訊 (這很小，不會崩潰)
    json_payload = json.dumps(meta_data, ensure_ascii=False)
    final_html = html_code.replace("const src = [];", f"const src = {json_payload};")
    
    # 監聽 HTML 回傳的點擊事件
    res = components.html(final_html, height=600, scrolling=True)
