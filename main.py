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
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")

# 確保必要的資料夾存在
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# --- 2. 核心功能：同步 PDF 與 數據快取 ---
def sync_data():
    if os.path.exists(CACHE_CSV):
        df_cache = pd.read_csv(CACHE_CSV)
    else:
        df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_entries = []

    for pdf in all_pdfs:
        if pdf not in df_cache['文件名'].values:
            with st.spinner(f'偵測到新報告，解析中: {pdf}...'):
                try:
                    info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
                    info["文件名"] = pdf
                    # 若解析不到日期，使用當前日期
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

# --- 3. 登入驗證功能 (含使用期限判斷) ---
def check_login(username, password):
    if not os.path.exists(USER_DB):
        st.error(f"錯誤：找不到帳號設定檔 {USER_DB}")
        return False
    
    try:
        users_df = pd.read_csv(USER_DB)
        # 尋找匹配的帳號與密碼 (轉成字串比對)
        match = users_df[(users_df['account'].astype(str) == str(username)) & 
                         (users_df['password'].astype(str) == str(password))]
        
        if not match.empty:
            # 檢查使用期限 expiry_date
            expiry_str = str(match.iloc[0]['expiry_date']).strip()
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                if date.today() <= expiry_date:
                    return True  # 沒過期
                else:
                    st.error(f"❌ 您的帳號已於 {expiry_str} 到期，請聯繫管理員續約。")
                    return False
            except ValueError:
                st.error("❌ 帳號檔案日期格式錯誤，請使用 YYYY-MM-DD")
                return False
        return False
    except Exception as e:
        st.error(f"讀取登入資訊時出錯: {e}")
        return False

# --- 4. 介面邏輯控制 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    #
