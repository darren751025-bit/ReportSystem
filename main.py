import streamlit as st
import os
import base64
from parsers import extract_financial_data

# 頁面基本設定
st.set_page_config(layout="wide", page_title="證券研究報告檢索系統")

# 路徑設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

def get_pdf_download_link(file_path, file_name):
    """生成一個點擊即可預覽/下載的連結"""
    with open(file_path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" target="_blank" style="text-decoration:none; background-color:#4CAF50; color:white; padding:8px 16px; border-radius:5px;">開啟報告</a>'
        return href

st.title("📂 證券研究報告管理系統")

# 1. 偵測檔案
if not os.path.exists(REPORT_DIR):
    st.error(f"找不到 reports 資料夾，請確認路徑：{REPORT_DIR}")
else:
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    
    if not files:
        st.warning("reports 資料夾內沒有 PDF 檔案。")
    else:
        st.success(f"已偵測到 {len(files)} 份報告")
        
        # 2. 準備表格資料
        table_data = []
        for f in files:
            full_path = os.path.join(REPORT_DIR, f)
            # 呼叫解析器
            info = extract_financial_data(full_path)
            
            # 生成預覽連結
            link_html = get_pdf_download_link(full_path, f)
            
            # 整理成表格格式
            table_data.append({
                "日期": info.get("日期", "-"),
                "代號": info.get("代號", "-"),
                "名稱": info.get("名稱", "-"),
                "券商": info.get("券商", "-"),
                "建議": info.get("建議", "-"),
                "目標價": info.get("目標價", "-"),
                "檔案連結": link_html
            })

        # 3. 顯示表格 (使用 Streamlit 原生 Markdown 渲染，避開 ERR_BLOCKED_BY_CLIENT)
        # 我們將 HTML 注入 Markdown 列表中
        st.write("---")
        
        # 建立表頭
        cols = st.columns([1, 1, 2, 1, 1, 1, 1])
        headers = ["日期", "代號", "名稱", "券商", "建議", "目標價", "操作"]
        for col, h in zip(cols, headers):
            col.write(f"**{h}**")
            
        st.write("---")

        # 逐行顯示
        for row in table_data:
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 2, 1, 1, 1, 1])
            c1.write(row["日期"])
            c2.write(row["代號"])
            c3.write(row["名稱"])
            c4.write(row["券商"])
            c5.write(row["建議"])
            c6.write(f":red[{row['目標價']}]")
            c7.markdown(row["檔案連結"], unsafe_allow_html=True)
