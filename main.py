import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
from datetime import date
from parsers import extract_financial_data

# 1. 頁面配置
st.set_page_config(layout="wide", page_title="證券研究報告系統")

# --- 2. 側邊欄：過濾與登入 ---
with st.sidebar:
    st.header("🔍 篩選與管理")
    
    # 時間篩選器
    st.subheader("報告日期範圍")
    d_range = st.date_input(
        "選擇區間",
        [date(2024, 1, 1), date.today()],
        key="date_range"
    )
    
    st.markdown("---")
    st.subheader("🔐 會員中心")
    st.text_input("帳號", placeholder="Admin")
    st.text_input("密碼", type="password")
    if st.button("確認登入", use_container_width=True):
        st.toast("連線成功")

# --- 3. 載入外觀樣式 (test001.html) ---
try:
    with open("test001.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=120)
except:
    st.title("證券研究報告檢索系統")

# --- 4. 檔案處理邏輯 ---
REPORT_DIR = "reports"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)
    st.info("請將 PDF 檔案放入 reports 資料夾後重新整理。")
else:
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    
    if files:
        # 解析所有檔案
        all_data = []
        for f in files:
            res = extract_financial_data(os.path.join(REPORT_DIR, f))
            res["file_id"] = f # 記錄檔名供下載使用
            all_data.append(res)
        
        df = pd.DataFrame(all_data)
        
        # 執行時間篩選
        if isinstance(d_range, list) and len(d_range) == 2:
            df = df[(df['日期'] >= d_range[0]) & (df['日期'] <= d_range[1])]

        st.write(f"📂 目前顯示 **{len(df)}** 份報告")

        # --- 5. 卡片式版面顯示 (三欄) ---
        cols = st.columns(3)
        for idx, row in df.reset_index().iterrows():
            with cols[idx % 3]:
                # 這裡使用 HTML 呈現卡片樣式
                st.markdown(f"""
                <div style="background: white; border-radius: 10px; padding: 15px; border: 1px solid #ddd; margin-bottom: 10px;">
                    <div style="color: #1e3a8a; font-weight: bold;">{row['名稱']}</div>
                    <div style="font-size: 0.85em; color: #666; margin-top: 5px;">
                        📅 {row['日期']} | 🏢 {row['券商']}
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9em;">
                        建議：<b>{row['建議']}</b> | 目標價：<span style="color:red;">{row['目標價']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 原生下載按鈕
                with open(os.path.join(REPORT_DIR, row['file_id']), "rb") as f_bytes:
                    st.download_button(
                        label=f"📥 下載報告",
                        data=f_bytes,
                        file_name=row['file_id'],
                        key=f"dl_{idx}",
                        use_container_width=True
                    )
    else:
        st.warning("reports 資料夾內尚無 PDF 檔案。")
