import streamlit as st
import os, json, base64
import streamlit.components.v1 as components

# 設定頁面
st.set_page_config(layout="wide")

# 路徑設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
HTML_PATH = os.path.join(BASE_DIR, "test.html")

def get_b64(path):
    try:
        with open(path, "rb") as f:
            # 限制讀取大小，避免記憶體當機 (測試用)
            return base64.b64encode(f.read()).decode()
    except:
        return ""

st.title("🚀 系統診斷控制台")

# 第一步：檢查資料夾
if not os.path.exists(REPORT_DIR):
    st.error(f"找不到 reports 資料夾，請確認路徑：{REPORT_DIR}")
    st.stop()

files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]

# 在 Streamlit 原生介面顯示檔案列表 (確認 Python 真的有抓到檔案)
with st.sidebar:
    st.subheader("📁 偵測到檔案")
    st.write(files if files else "無 PDF 檔案")

# 第二步：建立資料
all_data = []
for f in files:
    full_path = os.path.join(REPORT_DIR, f)
    all_data.append({
        "filename": f,
        "代號": f.split('.')[0],
        "pdfData": f"data:application/pdf;base64,{get_b64(full_path)}"
    })

# 第三步：渲染 HTML
if os.path.exists(HTML_PATH):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    
    # 注入資料
    json_payload = json.dumps(all_data, ensure_ascii=False)
    # 這裡是關鍵：我們改用自定義標籤來替換
    final_html = template.replace("/*DATA_PLACEHOLDER*/", f"const src = {json_payload};")
    
    components.html(final_html, height=1000, scrolling=True)
else:
    st.error("找不到 test.html")
