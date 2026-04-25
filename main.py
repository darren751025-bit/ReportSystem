import streamlit as st
import os
import pandas as pd
from parsers import extract_financial_data

# 1. 頁面基本設定 (原始設定)
st.set_page_config(layout="wide", page_title="券商報告檢索系統")

# --- 2. 原始側邊欄 ---
st.sidebar.title("👤 會員登入")
user = st.sidebar.text_input("帳號")
pw = st.sidebar.text_input("密碼", type="password")
if st.sidebar.button("登入"):
    st.sidebar.success(f"歡迎登入, {user}")

st.title("📂 研究報告檢索系統")

# --- 3. 路徑設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# 檢查資料夾
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)
    st.info("請將 PDF 檔案放入 reports 資料夾")
else:
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    
    if not files:
        st.warning("目前沒有偵測到 PDF 檔案")
    else:
        # 4. 讀取與解析
        all_data = []
        for f in files:
            f_path = os.path.join(REPORT_DIR, f)
            # 呼叫最穩定的解析器
            res = extract_financial_data(f_path)
            res["檔案名稱"] = f
            all_data.append(res)
        
        # 5. 顯示表格 (使用最穩定的 st.dataframe)
        df = pd.DataFrame(all_data)
        st.subheader("報告列表")
        st.dataframe(df, use_container_width=True)

        # 6. 下載功能 (原生下載，不透過 HTML)
        st.write("---")
        st.subheader("📥 檔案下載")
        selected_file = st.selectbox("選擇要下載的檔案", files)
        with open(os.path.join(REPORT_DIR, selected_file), "rb") as f:
            st.download_button(
                label=f"點此下載 {selected_file}",
                data=f,
                file_name=selected_file,
                mime="application/pdf"
            )

st.write("---")
st.caption("系統狀態：復原模式 (無外部依賴)")
