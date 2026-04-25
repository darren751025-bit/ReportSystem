import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
from parsers import extract_financial_data
from datetime import datetime

# 頁面配置
st.set_page_config(layout="wide", page_title="券商研究系統 V2")

# --- 側邊欄：時間選擇與登入 ---
st.sidebar.title("🔍 系統過濾")
start_date = st.sidebar.date_input("起始日期", datetime(2024, 1, 1))
end_date = st.sidebar.date_input("結束日期", datetime.now())

st.sidebar.markdown("---")
st.sidebar.subheader("👤 會員中心")
st.sidebar.text_input("帳號")
st.sidebar.text_input("密碼", type="password")
st.sidebar.button("登入系統")

# --- 主視覺區域 (載入 test001.html) ---
try:
    with open("test001.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=150)
except:
    st.title("證券研究報告系統")

# --- 檔案處理邏輯 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

if os.path.exists(REPORT_DIR):
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    
    if files:
        all_data = []
        for f in files:
            res = extract_financial_data(os.path.join(REPORT_DIR, f))
            res["filename"] = f
            all_data.append(res)
        
        # 轉換 DataFrame 並進行時間過濾
        df = pd.DataFrame(all_data)
        # 確保日期格式正確以便過濾
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        filtered_df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]

        # --- 卡片式版面顯示 ---
        st.subheader(f"📊 搜尋結果 ({len(filtered_df)} 份報告)")
        
        # 每列顯示 3 個卡片
        cols = st.columns(3)
        for idx, row in filtered_df.iterrows():
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"""
                    <div style="border:1px solid #e6e6e6; border-radius:10px; padding:15px; margin-bottom:10px; background-color:white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <h4 style="margin:0; color:#1e3a8a;">{row['名稱']}</h4>
                        <p style="font-size:0.9em; color:gray;">📅 日期: {row['日期']} | 🏢 券商: {row['券商']}</p>
                        <hr style="margin:10px 0;">
                        <p><b>建議：</b> {row['建議']} | <b>目標價：</b> <span style="color:red;">{row['目標價']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 下載按鈕放卡片下方
                    with open(os.path.join(REPORT_DIR, row['filename']), "rb") as b:
                        st.download_button(
                            label=f"📥 下載報告",
                            data=b,
                            file_name=row['filename'],
                            key=f"dl_{idx}"
                        )
    else:
        st.info("請在 reports 資料夾中放入 PDF 檔案。")
else:
    st.error("系統路徑錯誤：找不到 reports 資料夾。")
