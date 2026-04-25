import streamlit as st
import os, json, base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# 獲取絕對路徑
current_path = os.path.dirname(os.path.abspath(__file__))
report_path = os.path.join(current_path, "reports")
html_path = os.path.join(current_path, "test.html")

st.title("🔍 系統路徑診斷")

# 診斷資訊 (這會出現在 Streamlit 網頁最上方)
st.info(f"目前執行資料夾: {current_path}")

if not os.path.exists(report_path):
    st.error(f"❌ 找不到 reports 資料夾！請確認它在: {report_path}")
    files = []
else:
    files = [f for f in os.listdir(report_path) if f.lower().endswith('.pdf')]
    st.success(f"✅ 找到 {len(files)} 個 PDF 檔案")

# 讀取 PDF 並轉 Base64
all_reports = []
for f in files:
    full_p = os.path.join(report_path, f)
    with open(full_p, "rb") as pdf_file:
        b64 = base64.b64encode(pdf_file.read()).decode()
    all_reports.append({
        "filename": f,
        "pdf": f"data:application/pdf;base64,{b64}"
    })

# 注入 HTML
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    
    # 用最原始的替換方式
    json_str = json.dumps(all_reports, ensure_ascii=False)
    final_html = html_code.replace("const src = [];", f"const src = {json_str};")
    
    components.html(final_html, height=800, scrolling=True)
else:
    st.error("❌ 找不到 test.html")
