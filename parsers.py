import pdfplumber
import re

def extract_financial_data(file_path):
    """
    從 PDF 提取文字資訊，不包含任何 Base64 數據
    """
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
                # 簡單的正則表達式範例 (請根據你的 PDF 格式調整)
                # 1. 抓取日期 (格式如 2026/3/12)
                date_match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', text)
                if date_match: data["日期"] = date_match.group(1)
                
                # 2. 抓取券商名稱 (範例：尋找「投顧」二字)
                if "永豐" in text: data["券商"] = "永豐投顧"
                elif "Morgan Stanley" in text: data["券商"] = "大摩 (MS)"
                
                # 3. 抓取個股名稱與代號 (範例：M31 (6643))
                stock_match = re.search(r'([A-Z0-9]+)\s*\((\d{4})\)', text)
                if stock_match:
                    data["名稱"] = stock_match.group(1)
                    data["代號"] = stock_match.group(2)
                
                # 4. 抓取投資建議與目標價
                if "中立" in text: data["建議"] = "中立"
                elif "買進" in text or "Overweight" in text: data["建議"] = "買進"
                
                price_match = re.search(r'(?:目標價|Target Price).*?(\d+[\d,.]*)', text)
                if price_match: data["目標價"] = price_match.group(1)
                
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        
    return data
