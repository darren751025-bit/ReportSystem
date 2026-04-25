import streamlit as st
import os, json, base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="DEBUG 測試版")

# 獲取路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
HTML_PATH = os.path.join(BASE_DIR, "test.html")

def get_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def load_simple_data():
    if not os.path.exists(REPORT_DIR):
        return []
    
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    data_list = []
    
    for f in files:
        # 先建立基礎資料，避免解析失敗導致整格消失
        item = {
            "日期": "2026/04/25",
            "代號": f.split('.')[0], # 用檔名當代號測試
            "名稱": "測試檔案",
            "券商": "偵測中",
            "建議": "持有",
            "目標價": "-",
            "昨收": "-",
            "pdfData": f"data:application/pdf;base64,{get_b64(os.path.join(REPORT_DIR, f))}",
            "filename": f
        }
        data_list.append(item)
    return data_list

st.title("🛠️ 系統除錯模式")

if not os.path.exists(HTML_PATH):
    st.error(f"找不到 test.html (路徑: {HTML_PATH})")
else:
    reports = load_simple_data()
    
    if not reports:
        st.warning(f"目前在 {REPORT_DIR} 裡面沒看到 PDF 檔案。")
    else:
        st.success(f"成功偵測到 {len(reports)} 個檔案，準備渲染。")
        
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        json_data = json.dumps(reports, ensure_ascii=False)
        # 強制替換
        final_html = html_content.replace("const src = [];", f"const src = {json_data};")
        
        components.html(final_html, height=800, scrolling=True)
