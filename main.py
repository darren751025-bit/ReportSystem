import streamlit as st
import os
import pandas as pd
from parsers import extract_financial_data

st.set_page_config(layout="wide", page_title="券商報告系統")

# --- 側邊欄：登入資訊 ---
st.sidebar.title("👤 會員中心")
if st.sidebar.checkbox("管理員登入"):
    st.sidebar.text_input("帳號")
    st.sidebar.text_input("密碼", type="password")
    st.sidebar.button("登入")

st.title("📂 證券研究報告檢索系統")

# --- 讀取檔案 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

if not os.path.exists(REPORT_DIR):
    st.error(f"路徑錯誤：請建立 `{REPORT_DIR}` 資料夾並放入 PDF")
else:
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    
    if not files:
        st.info("目前資料夾中沒有 PDF 檔案")
    else:
        all_results = []
        # 進度條，讓使用者知道系統正在跑
        progress_bar = st.progress(0)
        
        for i, f in enumerate(files):
            f_path = os.path.join(REPORT_DIR, f)
            # 解析
            res = extract_financial_data(f_path)
            res["原始檔名"] = f
            all_results.append(res)
            progress_bar.progress((i + 1) / len(files))
        
        # 轉成表格
        df = pd.DataFrame(all_results)
        
        # --- 搜尋功能 ---
        search = st.text_input("🔍 搜尋公司名稱或代號", "")
        if search:
            df = df[df['名稱'].str.contains(search) | df['代號'].str.contains(search)]
        
        # --- 顯示表格 ---
        st.subheader(f"📊 報告總覽 (共 {len(df)} 筆)")
        # 使用原生表格，避免所有 ERR_BLOCKED_BY_CLIENT 錯誤
        st.dataframe(df, use_container_width=True)
        
        # --- 下載區 ---
        st.write("---")
        st.subheader("📥 取得檔案")
        col1, col2 = st.columns([3, 1])
        with col1:
            to_download = st.selectbox("選擇要下載的檔案", files)
        with col2:
            with open(os.path.join(REPORT_DIR, to_download), "rb") as f:
                st.download_button("💾 下載 PDF", data=f, file_name=to_download)

st.write("---")
st.caption("系統狀態：運行中 | 無外部 HTML 依賴")
