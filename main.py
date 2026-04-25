import streamlit as st
import os
import pandas as pd
from datetime import date
from parsers import extract_financial_data

# 頁面基本配置
st.set_page_config(layout="wide", page_title="證券研究報告系統 V3")

# --- 側邊欄：搜尋與過濾 ---
with st.sidebar:
    st.header("🔍 系統過濾器")
    # 日期範圍選擇器
    st.subheader("設定報告時間")
    start_dt = st.date_input("開始日期", date(2024, 1, 1))
    end_dt = st.date_input("結束日期", date.today())
    
    st.divider()
    st.subheader("🔐 管理員登入")
    st.text_input("帳號")
    st.text_input("密碼", type="password")
    if st.button("連線檢查", use_container_width=True):
        st.toast("連線中...", icon="🔄")

# --- 注入 CSS 樣式 (讀取 test.html) ---
try:
    with open("test.html", "r", encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)
except FileNotFoundError:
    st.error("找不到 test.html，請確認檔案名稱是否正確。")

# 標題橫幅
st.markdown('<div class="header-banner"><h1>📂 證券研究報告檢索系統</h1><p>已切換至 test.html 穩定傳輸架構</p></div>', unsafe_allow_html=True)

# --- 資料處理與顯示 ---
REPORT_DIR = "reports"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)
    st.info("請將 PDF 報告放入 reports 資料夾後重新整理。")
else:
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    
    if files:
        all_data = []
        for f in files:
            all_data.append(extract_financial_data(os.path.join(REPORT_DIR, f)))
        
        df = pd.DataFrame(all_data)
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        
        # 過濾日期
        df = df[(df['日期'] >= start_dt) & (df['日期'] <= end_dt)]
        df = df.sort_values(by="日期", ascending=False)

        st.subheader(f"📊 目前共有 {len(df)} 份研究報告符合條件")

        # --- 雙欄佈局 ---
        col1, col2 = st.columns(2)
        
        for idx, (orig_idx, row) in enumerate(df.iterrows()):
            target_col = col1 if idx % 2 == 0 else col2
            
            with target_col:
                st.markdown(f"""
                <div class="report-card">
                    <div class="card-title">{row['名稱']}</div>
                    <p style="color: gray; font-size: 0.9rem;">
                        📅 報告日期：{row['日期']} | 🏢 券商：{row['券商']}
                    </p>
                    <p>建議：<b>{row['建議']}</b> | 目標價：<span class="price-tag">{row['目標價']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # 原生下載按鈕
                with open(os.path.join(REPORT_DIR, row['名稱']), "rb") as f_bytes:
                    st.download_button(
                        label=f"📥 下載報告檔案",
                        data=f_bytes,
                        file_name=row['名稱'],
                        key=f"dl_{idx}",
                        use_container_width=True
                    )
                st.write("") 
    else:
        st.warning("reports 資料夾內尚無 PDF 檔案。")

st.divider()
st.caption("提示：若網頁顯示錯誤，請關閉瀏覽器的廣告攔截插件並重新整理。")
