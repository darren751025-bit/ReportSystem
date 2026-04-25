import pdfplumber
import re

# 直接定義函式，不要在檔案內 import 自己
def extract_financial_data(pdf_path):
    data = {
        "代號": "",
        "名稱": "",
        "券商": "",
        "建議": "",
        "目標價": "",
        "昨收": ""
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            if text:
                # 這裡放你的正則表達式解析邏輯 (以下為範例)
                # 提取券商
                if "元大" in text: data["券商"] = "元大"
                elif "凱基" in text: data["券商"] = "凱基"
                
                # 提取代號與名稱 (例如: 台積電(2330))
                match_stock = re.search(r'([\u4e00-\u9fa5]+)\s*\((\d{4})\)', text)
                if match_stock:
                    data["名稱"] = match_stock.group(1)
                    data["代號"] = match_stock.group(2)

    except Exception as e:
        print(f"解析錯誤: {e}")
        
    return data
