import pdfplumber

def extract_financial_data(file_path):
    """
    最基礎的解析邏輯，僅提取文字，不處理任何預覽數據。
    """
    # 預設回傳格式
    data = {
        "日期": "-",
        "代號": "-",
        "名稱": "-",
        "券商": "-",
        "建議": "-",
        "目標價": "-"
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            if text:
                # 如果有讀到字，暫時統一標記為已讀取
                # (你可以之後再慢慢加回正則表達式)
                data["名稱"] = "已讀取PDF內容"
    except Exception as e:
        # 發生錯誤時只印在後台，不讓前台崩潰
        print(f"Error reading {file_path}: {e}")
        
    return data
