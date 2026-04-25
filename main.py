import streamlit as st
import os

# 1. 頁面配置
st.set_page_config(page_title="系統重置測試")

# --- 側邊欄 ---
st.sidebar.title("測試模式")
if st.sidebar.button("點擊測試"):
    st.sidebar.write("按鈕正常")

# --- 主畫面 ---
st.title("🚀 系統回歸原始狀態")
st.write("如果你看到這個畫面，代表 Streamlit 運行正常，沒有次數問題。")

# 2. 顯示檔案清單就好，先不要解析
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

if os.path.exists(REPORT_DIR):
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    st.success(f"資料夾連線正常，目前有 {len(files)} 份檔案")
    for f in files:
        st.write(f"📄 {f}")
else:
    st.error("找不到 reports 資料夾")
