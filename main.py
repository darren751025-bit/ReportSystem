import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from parsers import extract_financial_data

# --- 基礎設定 ---
st.set_page_config(page_title="ReportSystem 報告檢索系統", layout="wide")

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
USER_DB = os.path.join(BASE_DIR, "data", "users.csv")

# --- 核心功能：自動同步資料庫 ---
def sync_data():
    if not os.path.exists(PDF_FOLDER): os.makedirs(PDF_FOLDER)
    
    # 讀取現有快取
    if os.path.exists(CACHE_CSV):
        df_cache = pd.read_csv(CACHE_CSV)
    else:
        df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_data = []

    for pdf in all_pdfs:
        # 如果 PDF 還沒在 CSV 紀錄裡，就解析它
        if pdf not in df_cache['文件名'].values:
            with st.spinner(f'正在解析新報告: {pdf}...'):
                info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
                info["文件名"] = pdf
                info["日期"] = datetime.now().strftime("%m.%d")
                new_data.append(info)
    
    if new_data:
        df_new = pd.DataFrame(new_data)
        df_cache = pd.concat([df_cache, df_new], ignore_index=True)
        df_cache.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    
    return df_cache

# --- 登入介面 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔒 ReportSystem 登入")
    user = st.text_input("帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("登入"):
        # 簡單驗證邏輯 (你可以改為讀取 users.csv)
        if user == "admin" and pw == "8888":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")
else:
    # --- 主程式介面 ---
    df = sync_data()

    # 側邊欄：進階篩選
    with st.sidebar:
        st.header("🎯 進階篩選")
        search_q = st.text_input("搜尋代號或名稱", "")
        broker_filter = st.multiselect("選擇券商", options=df['券商'].unique())
        st.divider()
        st.info("提示：上傳 PDF 至 GitHub reports 資料夾後，重新整理此頁面即可自動更新。")

    # 上方導覽標籤 (符合目標圖片)
    st.title("📊 券商研究報告檢索系統")
    tabs = st.tabs(["全部報告", "個股報告", "晨會報告", "產業報告"])

    with tabs[0]:
        # 套用篩選
        display_df = df.copy()
        if search_q:
            display_df = display_df[display_df['代號'].astype(str).str.contains(search_q) | 
                                    display_df['名稱'].str.contains(search_q)]
        if broker_filter:
            display_df = display_df[display_df['券商'].isin(broker_filter)]

        # 顯示專業表格
        st.dataframe(
            display_df[["日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"]],
            use_container_width=True,
            hide_index=True
        )

        # 底部：查看 PDF 功能
        st.subheader("📖 查看原始報告")
        selected_pdf = st.selectbox("請選擇要開啟的報告檔名", display_df['文件名'].tolist())
        
        if selected_pdf:
            pdf_path = os.path.join(PDF_FOLDER, selected_pdf)
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            
            # 使用 HTML 嵌入 PDF
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)
