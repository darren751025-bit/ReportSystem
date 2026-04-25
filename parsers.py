import streamlit as st
import pandas as pd
import os
from datetime import datetime
from parsers import extract_financial_data # 引用剛才寫的解析引擎

# 設定
st.set_page_config(page_title="券商研究報告系統", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "reports")
CACHE_CSV = os.path.join(BASE_DIR, "data", "report_cache.csv")

# --- 自動更新資料庫邏輯 ---
def update_database():
    if not os.path.exists(PDF_FOLDER): os.makedirs(PDF_FOLDER)
    
    # 讀取現有快取
    if os.path.exists(CACHE_CSV):
        df_cache = pd.read_csv(CACHE_CSV)
    else:
        df_cache = pd.DataFrame(columns=["文件名", "日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"])

    all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    new_data = []

    for pdf in all_pdfs:
        if pdf not in df_cache['文件名'].values:
            # 發現新檔案，啟動解析器
            st.info(f"正在自動解析新報告: {pdf}...")
            info = extract_financial_data(os.path.join(PDF_FOLDER, pdf))
            info["文件名"] = pdf
            info["日期"] = datetime.now().strftime("%m.%d")
            new_data.append(info)
    
    if new_data:
        df_new = pd.DataFrame(new_data)
        df_cache = pd.concat([df_cache, df_new], ignore_index=True)
        df_cache.to_csv(CACHE_CSV, index=False, encoding='utf-8-sig')
    
    return df_cache

# --- 介面呈現 ---
st.title("📑 券商研究報告總覽")

# 分類標籤 (如目標圖片)
tabs = st.tabs(["全部", "個股報告", "晨會報告", "產業報告"])

with tabs[0]:
    df = update_database()
    
    # 搜尋與篩選列
    col_s1, col_s2 = st.columns([1, 3])
    search_code = col_s1.text_input("🔍 代號搜尋")
    
    display_df = df.copy()
    if search_code:
        display_df = display_df[display_df['代號'].astype(str).str.contains(search_code)]

    # 顯示美化表格
    st.dataframe(
        display_df[["日期", "代號", "名稱", "券商", "建議", "目標價", "昨收"]],
        use_container_width=True,
        hide_index=True
    )

    # 點擊開啟功能
    st.divider()
    selected_file = st.selectbox("選擇要查看的 PDF", display_df['文件名'].tolist())
    if st.button("直接打開選中報告"):
        # 這裡套用之前教你的下載/開啟邏輯
        st.write(f"正在開啟: {selected_file}")
