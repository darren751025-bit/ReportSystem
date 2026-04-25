import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import base64
from parsers import extract_financial_data

# --- 1. 系統路徑與基礎設定 ---
st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")

# 確保資料夾結構正確
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(CACHE_CSV), exist_ok=True)

# --- 2. 核心邏輯：同步 PDF 資料 ---
def sync_data():
    # 讀取快取，若無則建立新表格
    if os.path.exists(CACHE_CSV):
        try:
            df_cache = pd.read_csv(CACHE_CSV)
        except:
            df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])
    else:
        df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])

    # 掃描資料夾內的 PDF
    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_entries = []

    for pdf in all_pdfs:
        if pdf not in df_cache['文件名'].values:
            with st.spinner(f'解析新報告中: {pdf}...'):
                try:
                    # 呼叫 parsers.py 的解析引擎
                    info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
                    info["文件名"] = pdf
                    if not info.get("日期"):
                        info["日期"] = datetime.now().strftime("%m.%d")
                    new_entries.append(info)
                except Exception as e:
                    st.error(f"檔案 {pdf} 解析失敗: {e}")
    
    if new_entries:
        df_new = pd.DataFrame(new_entries)
        df_cache = pd.concat([df_cache, df_new], ignore_index=True)
        df_cache.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    
    return df_cache

# --- 3. 權限邏輯：登入與日期檢查 ---
def check_login(username, password):
    if not os.path.exists(USER_DB):
        st.error(f"找不到會員資料檔：{USER_DB}")
        return False
    
    try:
        users_df = pd.read_csv(USER_DB)
        # 過濾帳號密碼 (支援數字與字串混合比對)
        match = users_df[(users_df['account'].astype(str) == str(username)) & 
                         (users_df['password'].astype(str) == str(password))]
        
        if not match.empty:
            # 檢查使用期限
            expiry_str = str(match.iloc[0]['expiry_date']).strip()
            expiry_date_val = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            
            if date.today() <= expiry_date_val:
                return True
            else:
                st.warning(f"您的帳號已於 {expiry_str} 到期，請聯絡管理員。")
                return False
        return False
    except Exception as e:
        st.error(f"登入驗證發生錯誤：{e}")
        return False

# --- 4. 介面呈現與操作流程 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    # 登入介面
    st.title("🔒 研究報告檢索系統 - 會員登入")
    with st.form("login_panel"):
        u = st.text_input("帳號 (Account)")
        p = st.text_input("密碼 (Password)", type="password")
        if st.form_submit_button("進入系統", use_container_width=True):
            if check_login(u, p):
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("登入失敗：帳號密碼錯誤或使用期限已過期。")
else:
    # 登入後的內容
    df_data = sync_data()

    # 側邊欄控制
    with st.sidebar:
        st.header("⚙️ 篩選控制項")
        keyword = st.text_input("搜尋代號或股票名稱")
        st.divider()
        if st.button("登出系統"):
            st.session_state['logged_in'] = False
            st.rerun()

    # 主顯示區
    st.title("📊 券商研究報告檢索平台")
    
    tab1, tab2, tab3 = st.tabs(["全部報告", "個股研究", "產業/晨報"])

    with tab1:
        # 資料篩選
        display_df = df_data.copy()
        if keyword:
            mask = display_df.apply(lambda row: row.astype(str).str.contains(keyword).any(), axis=1)
            display_df = display_df[mask]

        # 表格顯示
        st.dataframe(
            display_df[["日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"]],
            use_container_width=True,
            hide_index=True
        )

        # PDF 開啟預覽
        st.divider()
        st.subheader("📄 報告原文預覽")
        if not display_df.empty:
            pick_pdf = st.selectbox("選取報告檔名進行預覽", display_df['文件名'].tolist())
            if pick_pdf:
                pdf_path = os.path.join(PDF_FOLDER, pick_pdf)
                with open(pdf_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.info("目前無報告可供顯示，請檢查 reports 資料夾。")
