import streamlit as st
import pandas as pd
import os
import json
import base64
from datetime import datetime
import streamlit.components.v1 as components
from parsers import extract_financial_data

# --- 基礎配置 ---
st.set_page_config(page_title="券商研究報告系統", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
HTML_FILE = os.path.join(BASE_DIR, "test.html")
USER_DB = os.path.join(BASE_DIR, "data", "Member account.csv")

os.makedirs(PDF_FOLDER, exist_ok=True)

def get_all_reports():
    if not os.path.exists(PDF_FOLDER):
        return []
    
    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    results = []
    
    for pdf in all_pdfs:
        try:
            path = os.path.join(PDF_FOLDER, pdf)
            info = extract_financial_data(path)
            
            # --- 加強文字搜尋邏輯 ---
            raw_rec = str(info.get("建議") or info.get("rec") or "")
            final_rec = "中立" # 預設
            
            buy_keywords = ["買進", "強力買進", "增加持股", "增持", "優於大盤", "Buy", "Outperform", "Accumulate"]
            sell_keywords = ["賣出", "降低持股", "減持", "劣於大盤", "Sell", "Underperform", "Reduce"]
            
            if any(k in raw_rec for k in buy_keywords):
                final_rec = "買進"
            elif any(k in raw_rec for k in sell_keywords):
                final_rec = "賣出"
            elif raw_rec:
                final_rec = raw_rec # 如果都不在清單但有抓到字，就顯示原始字樣

            # 將 PDF 轉為 base64 供預覽 (或簡單傳檔名)
            results.append({
                "date": str(info.get("日期") or datetime.now().strftime("%m.%d")),
                "code": str(info.get("代號") or ""),
                "name": str(info.get("名稱") or ""),
                "broker": str(info.get("券商") or ""),
                "rec": final_rec,
                "target": str(info.get("目標價") or "-"),
                "last": str(info.get("昨收") or "-"),
                "filename": pdf
            })
        except:
            continue
    return results

# --- 登入邏輯 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業報告檢索系統")
    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")
    if st.button("登入系統", use_container_width=True):
        if os.path.exists(USER_DB):
            users = pd.read_csv(USER_DB)
            if any((users['account'].astype(str)==u) & (users['password'].astype(str)==p)):
                st.session_state.auth = True
                st.rerun()
            else: st.error("帳密錯誤")
else:
    # --- 核心顯示 ---
    reports_data = get_all_reports()
    
    # 這裡很關鍵：為了讓 HTML 能下載 PDF，我們需要把 PDF 資料夾變成可存取的
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            tmpl = f.read()
        
        json_data_str = json.dumps(reports_data, ensure_ascii=False)
        final_html = tmpl.replace("const src = [];", f"const src = {json_data_str};")
        
        # 增加一個簡單的 Streamlit 下載功能 (在側邊欄)
        with st.sidebar:
            st.header("📂 檔案下載區")
            for r in reports_data:
                with open(os.path.join(PDF_FOLDER, r['filename']), "rb") as f:
                    st.download_button(label=f"⬇️ {r['name']}({r['code']})", data=f, file_name=r['filename'], key=r['filename'])
            if st.button("登出"):
                st.session_state.auth = False
                st.rerun()

        components.html(final_html, height=1000, scrolling=True)
