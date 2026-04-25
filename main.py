def check_login(username, password):
    if not os.path.exists(USER_DB):
        st.error("帳號設定檔不存在")
        return False
    
    try:
        # 讀取你的 Member account.csv
        users_df = pd.read_csv(USER_DB)
        
        # 尋找帳號與密碼匹配的資料
        match = users_df[(users_df['account'].astype(str) == str(username)) & 
                         (users_df['password'].astype(str) == str(password))]
        
        if not match.empty:
            # 取得該帳號的過期日期
            expiry_str = str(match.iloc[0]['expiry_date']).strip()
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            
            # 比對今天日期
            if date.today() <= expiry_date:
                return True # 沒過期，准許進入
            else:
                st.error(f"❌ 您的帳號已於 {expiry_str} 到期。")
                return False
        return False
    except Exception as e:
        st.error(f"登入系統出錯：{e}")
        return False
