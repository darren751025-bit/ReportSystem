import pdfplumber
import os
from datetime import datetime

def extract_financial_data(file_path):
    # 獲取檔案最後修改日期
    mtime = os.path.getmtime(file_path)
    file_date = datetime.fromtimestamp(mtime).date()
    
    # 預設回傳格式
    data = {
        "日期": file_date,
        "代號": "N/A",
        "名稱": os.path.basename(file_path),
        "券商": "偵測中",
        "建議": "中立",
        "目標價": "-"
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            if text:
                # 簡單內容識別邏輯
                if "SinoPac" in text or "永豐" in text: data["券商"] = "永豐投顧"
                elif "Morgan" in text or "MS" in text: data["券商"] = "大摩"
                
                # 這裡你可以後續加入正則表達式來精確抓取代號和目標價
    except Exception as e:
        print(f"解析 {file_path} 出錯: {e}")
        
    return data
