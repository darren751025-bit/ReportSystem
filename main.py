import streamlit as st
import os
import pandas as pd
from parsers import extract_financial_data

# 1. 頁面配置
st.set_page_config(layout="wide", page_title="券商報告檢索系統")

st.title("📂 券商研究報告檢索系統 (穩定版)")

# 2. 路徑設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# 3. 診斷與讀取
if not os.path.exists(REPORT_DIR):
    st.error(f"❌ 找不到資料夾: {REPORT_DIR}")
else:
    files = [f for f in os.listdir(REPORT_DIR) if f.lower().endswith(".pdf")]
    
    if not files:
        st.warning("⚠️ reports 資料夾內目前沒有 PDF 檔案。")
    else:
        st.sidebar.success(f"✅ 偵測到 {len(files)} 份報告")
        
        all_rows = []
        for f in files:
            file_path = os.path.join(REPORT_DIR, f)
            # 呼叫純文字解析器
            res = extract_financial_data(file_path)
            res["檔案名稱"] = f  # 保留原始檔名供參考
            all_rows.append(res)
        
        # 4. 將資料轉為 Pandas DataFrame
        df = pd.DataFrame(all_rows)
        
        # 5. 顯示搜尋/篩選功能 (Streamlit 原生)
        search_query = st.text_input("🔍 輸入個股代號或名稱進行搜尋", "")
        if search_query:
            df = df[df['名稱'].str.contains(search_query) | df['代號'].str.contains(search_query)]

        # 6. 最終表格呈現
        # 使用 st.dataframe 提供原生排序與篩選功能
        st.subheader("📊 報告列表")
        st.dataframe(
            df, 
            use_container_width=True,
            column_order=("日期", "代號", "名稱", "券商", "建議", "目標價", "檔案名稱")
        )

        # 7. 下載功能 (改用最安全的方法：Streamlit 原生下載按鈕)
        st.write("---")
        st.subheader("📥 取得檔案")
        selected_file = st.selectbox("選擇欲下載的報告", files)
        
        with open(os.path.join(REPORT_DIR, selected_file), "rb") as f:
            st.download_button(
                label=f"💾 下載 {selected_file}",
                data=f,
                file_name=selected_file,
                mime="application/pdf"
            )

# 8. 會員登入 (如果原本就有，會在這裡正常顯示)
st.sidebar.markdown("---")
if st.sidebar.button("系統管理登入"):
    st.sidebar.text_input("帳號")
    st.sidebar.text_input("密碼", type="password")
