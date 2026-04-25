import streamlit as st
import os, json, base64
import streamlit.components.v1 as components
from parsers import extract_financial_data

st.set_page_config(layout="wide", page_title="研究報告系統")

# 改用更正式的變數名，避開攔截器
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
# 建議將 test.html 改名為 index.html
HTML_PATH = os.path.join(BASE_DIR, "test.html") 

def get_b64_safe(path):
    with open(path, "rb") as f:
        # 使用 standard b64 確保格式正確
        return base64.b64encode(f.read()).decode('utf-8')

def get_data():
    if not os.path.exists(REPORT_FOLDER): return []
    files = [f for f in os.listdir(REPORT_FOLDER) if f.lower().endswith(".pdf")]
    res = []
    for f in files:
        path = os.path.join(REPORT_FOLDER, f)
        # 抓取解析後的文字資料
        info = extract_financial_data(path) 
        # 這裡不塞入 base64，避免 JSON 太大被攔截器砍掉
        info["id"] = f 
        res.append(info)
    return res

st.title("📂 證券研究報告管理系統")

# 顯示偵測狀態
data_list = get_data()
if not data_list:
    st.error(f"路徑偵測失敗或無 PDF 檔案: {REPORT_FOLDER}")
else:
    st.success(f"系統就緒：已偵測到 {len(data_list)} 份報告")

# 讀取 HTML 模板
if os.path.exists(HTML_PATH):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_code = f.read()
    
    # 注入純文字資料
    json_data = json.dumps(data_list, ensure_ascii=False)
    # 確保 HTML 裡的 const src = []; 這行沒有被攔截器過濾
    final_html = html_code.replace("const src = [];", f"const reportData = {json_data};")
    
    # 增加元件寬度，減少被誤判為邊欄廣告的機率
    components.html(final_html, height=900, scrolling=True)
else:
    st.warning("請確認 test.html 是否與 main.py 放在同一個資料夾")
