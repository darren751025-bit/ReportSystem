import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. 自動偵測路徑設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
USER_DB = os.path.join(BASE_DIR, "data", "users.csv")

# --- 2. 網頁頁面設定 ---
st.set_page_config(page_title="研究報告檢索系統", layout="wide")

# --- 3. 登入驗證函數 ---
def check_login(user, pwd):
    try:
        if not os.path.exists(USER_DB):
            return False, "找不到資料庫檔案"
        df = pd.read_csv(USER_DB)
        df['username'] = df['username'].astype(str)
        df['password'] = df['password'].astype(str)
        user_row = df[(df['username'] == str(user)) & (df['password'] == str(pwd))]
        
        if not user_row.empty:
            raw_date = str(user_row.iloc[0]['created_at'])
            date_str = raw_date.replace('/', '-') 
            start_date = pd.to_datetime(date_str).to_pydatetime()
            valid_days = int(user_row.iloc[0]['valid_days'])
            if (datetime.now() - start_date).days > valid_days:
                return False, "⚠️ 您的帳號已過期。"
            return True, "✅ 登入成功"
        return False, "❌ 帳號或密碼錯誤"
    except Exception as e:
        return False, f"系統錯誤: {e}"

# --- 4. 介面呈現邏輯 ---
if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

if not st.session_state['login_status']:
    st.title("🔒 會員登入")
    with st.form("login_form"):
        u = st.text_input("帳號")
        p = st.text_input("密碼", type="password")
        if st.form_submit_button("登入"):
            success, msg = check_login(u, p)
            if success:
                st.session_state['login_status'] = True
                st.rerun()
            else:
                st.error(msg)
else:
    st.sidebar.title("控制台")
    if st.sidebar.button("登出系統"):
        st.session_state['login_status'] = False
        st.rerun()

    st.title("📂 研究報告檢索系統")
    search_query = st.text_input("🔍 輸入關鍵字搜尋", "")

    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        
    all_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    filtered_files = [f for f in all_files if search_query.lower() in f.lower()]

    st.write(f"目前顯示 {len(filtered_files)} 份報告")
    st.divider()

    # --- 5. 修正後的顯示列表 ---
    for file_name in filtered_files:
        col1, col2 = st.columns([5, 1])
        col1.write(f"📄 {file_name}")
        
        file_path = os.path.join(PDF_FOLDER, file_name)
        
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            
            # 使用官方下載按鈕，這在 Windows 瀏覽器中相容性最高
            col2.download_button(
                label="打開報告",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf"
            )
        except Exception:
            col2.error("讀取失敗")
        st.divider()