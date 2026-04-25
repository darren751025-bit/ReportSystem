import streamlit as st
import json
import streamlit.components.v1 as components
from parsers import extract_financial_data
import os

# 1. 讀取並解析資料夾內的 PDF
def get_pdf_data():
    REPORT_DIR = "reports"
    results = []
    if os.path.exists(REPORT_DIR):
        files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
        for f in files:
            # 呼叫你現有的解析器
            data = extract_financial_data(os.path.join(REPORT_DIR, f))
            # 為了配合你的 HTML 下載功能，可以補一個路徑
            data['url'] = f"reports/{f}"
            results.append(data)
    return results

# 2. 啟動 Streamlit
st.set_page_config(layout="wide")

# 獲取資料並轉為 JSON 格式字串
data_json = json.dumps(get_pdf_data(), ensure_ascii=False)

# 3. 讀取 HTML 並注入資料
try:
    with open("test.html", "r", encoding="utf-8") as f:
        html_template = f.read()

    # 將資料直接塞進變數 originalData
    final_html = html_template.replace("[/* DATA_PLACEHOLDER */]", data_json)

    # 4. 渲染頁面 (高度設為 100vh 以配合你的設計)
    components.html(final_html, height=900, scrolling=True)

except Exception as e:
    st.error(f"錯誤: {e}")
