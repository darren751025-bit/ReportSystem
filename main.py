import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from parsers import extract_financial_data

# --- 基礎路徑設定 ---
st.set_page_config(page_title="ReportSystem 專業報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
# 更新：指向你改名後的成員帳號檔案
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")

# --- 核心功能：自動同步 PDF 與 資料庫 ---
def sync_data():
    if not os.path.exists(PDF_FOLDER): os.makedirs(PDF_FOLDER)
    
    if os.path.exists(CACHE_CSV):
        df_cache = pd.read_csv(CACHE_CSV)
    else:
        df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_entries = []

    for pdf in all_pdfs:
        if pdf not in df_cache['文件名'].values:
            with st.spinner(f'偵測到新報告，正在解析: {pdf}...'):
                info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
                info["文件名"] = pdf
                info["日期"] = datetime.now().strftime("%m.%d")
                new_entries.append(info)
    
    if new_entries:
        df_new = pd.DataFrame(new_entries)
        df_cache = pd.concat([df_cache, df_new], ignore_index=True)
        df_cache.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    
    return df_cache

# --- 登入驗證功能 ---
def check_login(username, password):
    if not os.path.exists(USER_DB):
        # 如果檔案不存在，建立一個預設檔
        df_default = pd.DataFrame([["admin", "8888"]], columns=["account", "password"])
        os.makedirs(os.path.dirname(USER_DB), exist_ok=True)
        df_default.to_csv(USER_DB, index=False)
        st.warning(f"找不到 {os.path.basename(USER_DB)}，已為您建立預設管理員帳號。")
        return username == "admin" and password == "8888"
    
    try:
        users_df = pd.read_csv(USER_DB)
        # 確保欄位名稱符合
        match = users_df[(users_df['account'] == username) & (users_df['password'].astype(str) == password)]
        return not match.empty
    except Exception as e:
        st.error(f"讀取帳號檔案失敗: {e}")
        return False

# --- 介面邏輯 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 ReportSystem 登入")
    with st.form("login_form"):
        u = st.text_input("帳號")
        p = st.text_input("密碼", type="password")
        if st.form_submit_button("登入系統"):
            if check_login(u, p):
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("帳號或密碼無效，請檢查 Member account.csv")
else:
    # 登入後的專業儀表板介面
    df = sync_data()

    # 側邊欄篩選器
    with st.sidebar:
        st.header("🔍 進階搜尋")
        search_term = st.text_input("輸入代號/名稱/券商")
        st.divider()
        st.caption("系統狀態: 運作中")
        if st.button("登出"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("📑 券商研究報告檢索系統")
    
    # 頂部導覽標籤
    tab_titles = ["全部報告", "個股報告", "晨會報告", "產業報告"]
    tabs = st.tabs(tab_titles)

    with tabs[0]:
        # 篩選邏輯
        display_df = df.copy()
        if search_term:
            mask = display_df.apply(lambda row: row.astype(str).str.contains(search_term).any(), axis=1)
            display_df = display_df[mask]

        # 顯示專業表格 (符合圖片中的欄位)
        st.dataframe(
            display_df[["日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"]],
            use_container_width=True,
            hide_index=True
        )

        # PDF 線上預覽區
        st.divider()
        st.subheader("👁️ 報告快速預覽")
        if not display_df.empty:
            target_pdf = st.selectbox("選擇要閱讀的報告", display_df['文件名'].tolist())
            
            if target_pdf:
                pdf_path = os.path.join(PDF_FOLDER, target_pdf)
                try:
                    with open(pdf_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"無法讀取 PDF 檔案: {e}")
        else:
            st.info("目前沒有符合篩選條件的報告。")
