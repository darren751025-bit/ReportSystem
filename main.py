import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import base64
from parsers import extract_financial_data

# --- 1. 基礎配置與路徑設定 ---
st.set_page_config(page_title="券商研究報告檢索系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")
# 指向你改名後的成員帳號檔案
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")

# 確保必要資料夾存在
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# --- 2. 核心功能：同步 PDF 數據 ---
def sync_data():
    if os.path.exists(CACHE_CSV):
        try:
            df_cache = pd.read_csv(CACHE_CSV)
        except:
            df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])
    else:
        df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_entries = []

    for pdf in all_pdfs:
        if pdf not in df_cache['文件名'].values:
            with st.spinner(f'解析新報告: {pdf}...'):
                try:
                    info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
                    info["文件名"] = pdf
                    if not info.get("日期"):
                        info["日期"] = datetime.now().strftime("%m.%d")
                    new_entries.append(info)
                except Exception as e:
                    st.error(f"解析 {pdf} 失敗: {e}")
    
    if new_entries:
        df_new = pd.DataFrame(new_entries)
        df_cache = pd.concat([df_cache, df_new], ignore_index=True)
        df_cache.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    
    return df_cache

# --- 3. 登入驗證功能 (包含日期限制與過期提醒) ---
def check_login(username, password):
    if not os.path.exists(USER_DB):
        st.error(f"找不到檔案：{USER_DB}")
        return False
    
    try:
        users_df = pd.read_csv(USER_DB)
        # 比對帳號與密碼
        match = users_df[(users_df['account'].astype(str) == str(username)) & 
                         (users_df['password'].astype(str) == str(password))]
        
        if not match.empty:
            # 取得該帳號的到期日
            expiry_str = str(match.iloc[0]['expiry_date']).strip()
            # 將字串轉為日期物件
            expiry_date_obj = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            
            # 檢查是否過期
            if date.today() <= expiry_date_obj:
                return True # 沒過期，登入成功
            else:
                # 這裡就是你要求的「過期顯示」
                st.error(f"❌ 您的帳號已於 {expiry_str} 到期，請聯繫管理員。")
                return False
        else:
            st.error("❌ 帳號或密碼錯誤。")
            return False
    except Exception as e:
        st.error(f"登入驗證出錯，請檢查 CSV 格式：{e}")
        return False

# --- 4. 介面控制流程 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    # 登入畫面
    st.title("🛡️ 報告檢索系統 - 會員登入")
    with st.container():
        u = st.text_input("帳號 (Account)")
        p = st.text_input("密碼 (Password)", type="password")
        if st.button("確認登入", use_container_width=True):
            if check_login(u, p):
                st.session_state['logged_in'] = True
                st.rerun()
else:
    # 登入成功後的主介面
    df = sync_data()

    with st.sidebar:
        st.header("🔍 篩選")
        search_q = st.text_input("搜尋代號/名稱")
        st.divider()
        if st.button("登出"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("📈 券商研究報告檢索平台")
    tabs = st.tabs(["全部報告", "個股研究", "產業報告"])

    with tabs[0]:
        display_df = df.copy()
        if search_q:
            mask = display_df.apply(lambda row: row.astype(str).str.contains(search_q).any(), axis=1)
            display_df = display_df[mask]

        st.dataframe(
            display_df[["日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"]],
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        if not display_df.empty:
            selected_pdf = st.selectbox("預覽 PDF 報告", display_df['文件名'].tolist())
            if selected_pdf:
                pdf_path = os.path.join(PDF_FOLDER, selected_pdf)
                with open(pdf_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
