import pdfplumber
import re

def extract_financial_data(file_path):
    # 預設值，確保不管發生什麼事都有東西回傳
    data = {"日期": "-", "代號": "-", "名稱": "-", "券商": "-", "建議": "-", "目標價": "-"}
    
    try:
        with pdfplumber.open(file_path) as pdf:
            text = pdf.pages[0].extract_text()
            if not text:
                return data
            
            # 1. 券商識別
            if "Morgan Stanley" in text:
                data["券商"] = "大摩 (MS)"
            elif "永豐" in text:
                data["券商"] = "永豐投顧"
            
            # 2. 日期抓取
            date_match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})|([A-Z][a-z]+ \d{1,2}, \d{4})', text)
            if date_match:
                data["日期"] = date_match.group(0)
            
            # 3. 代號與名稱
            # 針對 永豐格式: M31 (6643 TT)
            stock_match = re.search(r'([A-Z0-9]+)\s*\((\d{4})\s*TT\)', text)
            if stock_match:
                data["名稱"], data["代號"] = stock_match.groups()
            else:
                # 針對 大摩格式: Gold Circuit Electronics Ltd. (2368.TW)
                ms_stock = re.search(r'([A-Za-z\s]+)\s*\((\d{4})\.TW\)', text)
                if ms_stock:
                    data["名稱"], data["代號"] = ms_stock.groups()

            # 4. 投資建議 (買進/Overweight/中立)
            if "Overweight" in text or "買進" in text:
                data["建議"] = "買進"
            elif "中立" in text:
                data["建議"] = "中立"
            
            # 5. 目標價
            price_match = re.search(r'(?:Price Target|目標價).*?(?:NT\$|Target Price).*?(\d+[\d,.]*)', text, re.S)
            if price_match:
                data["目標價"] = price_match.group(1).replace(',', '')

    except Exception as e:
        # 如果解析某一檔案失敗，在後台印出錯誤，但不要弄斷網頁
        print(f"Error parsing {file_path}: {e}")
        
    return data
