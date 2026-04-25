import streamlit as st
import os
import pandas as pd
from parsers import extract_financial_data

# 頁面基本設定
st.set_page_config(layout="wide", page_title="券商研究報告系統")

# --- 側邊欄：登入功能 ---
with st.sidebar:
    st.title("👤 會員中心")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        user = st.text_input("帳號")
        pw = st.text_input("密碼", type="password")
        if st.button("登入"):
            # 這裡可以自定義帳密，目前預設點擊即登入
            st.session_state.logged_in = True
            st.rerun()
    else:
        st.success("已登入：管理員")
        if st.button("登出"):
            st.session_state.logged_in = False
            st.rerun()

# --- 主畫面邏輯 ---
st.title("📂 證券研究報告檢索系統")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# 確保資料夾存在
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)
    st.info(f"已自動建立資料夾：{REPORT_DIR}，請將 PDF 放入後重新整理。")

files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]

if not files:
    st.warning("目前 reports 資料夾內沒有任何 PDF 報告檔案。")
else:
    # 開始解析檔案
    all_data = []
    with st.spinner('正在讀取報告資料...'):
        for f in files:
            f_path = os.path.join(REPORT_DIR, f)
            res = extract_financial_data(f_path)
            res["檔案名稱"] = f
            all_data.append(res)
    
    df = pd.DataFrame(all_data)

    # --- 搜尋過濾器 ---
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        q = st.text_input("🔍 搜尋名稱/代號", "")
    with search_col2:
        broker = st.multiselect("過濾券商", df["券商"].unique())

    # 執行過濾
    filtered_df = df.copy()
    if q:
        filtered_df = filtered_df[filtered_df['名稱'].str.contains(q, case=False) | filtered_df['代號'].str.contains(q)]
    if broker:
        filtered_df = filtered_df[filtered_df['券商'].isin(broker)]

    # --- 資料展示 ---
    st.subheader(f"📊 報告列表 (共 {len(filtered_df)} 筆)")
    
    # 使用 st.dataframe 讓使用者可以點擊表頭排序
    st.dataframe(
        filtered_df, 
        use_container_width=True,
        column_config={
            "目標價": st.column_config.NumberColumn(format="NT$ %d"),
            "檔案名稱": "原始檔名"
        }
    )

    # --- 下載區塊 ---
    st.write("---")
    st.subheader("📥 檔案下載")
    selected_f = st.selectbox("請選擇要下載的報告", filtered_df["檔案名稱"].tolist())
    
    if selected_f:
        with open(os.path.join(REPORT_DIR, selected_f), "rb") as f:
            st.download_button(
                label=f"💾 下載 {selected_f}",
                data=f,
                file_name=selected_f,
                mime="application/pdf"
            )

st.write("---")
st.caption("系統狀態：核心運行中 (無外部 HTML 依賴)")
