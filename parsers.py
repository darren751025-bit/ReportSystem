import pdfplumber
import re

def extract_financial_data(file_path):
    # 初始預設值
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
            
            if not text:
                return data
            
            # --- 1. 判斷券商 ---
            if "SinoPac" in text or "永豐" in text:
                data["券商"] = "永豐投顧"
            elif "Morgan Stanley" in text:
                data["券商"] = "大摩 (MS)"
            
            # --- 2. 提取日期 ---
            # 匹配 2026/3/12 或 March 15, 2026
            date_match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})|([A-Z][a-z]+ \d{1,2}, \d{4})', text)
            if date_match:
                data["日期"] = date_match.group(0)
            
            # --- 3. 提取個股資訊 ---
            # 永豐格式: M31 (6643 TT)
            stock_yp = re.search(r'([A-Z0-9]+)\s*\((\d{4})\s*TT\)', text)
            # 大摩格式: Gold Circuit Electronics Ltd. (2368.TW)
            stock_ms = re.search(r'([A-Za-z0-9\s\.]+)\s*\((\d{4})\.(?:TW|SS)\)', text)
            
            if stock_yp:
                data["名稱"] = stock_yp.group(1)
                data["代號"] = stock_yp.group(2)
            elif stock_ms:
                data["名稱"] = stock_ms.group(1).strip()
                data["代號"] = stock_ms.group(2)
            
            # --- 4. 投資建議 ---
            if "Overweight" in text or "買進" in text:
                data["建議"] = "買進"
            elif "中立" in text or "In-Line" in text:
                data["建議"] = "中立"
            elif "Underweight" in text or "賣出" in text:
                data["建議"] = "賣出"
                
            # --- 5. 目標價 ---
            # 匹配 Target Price NT$1,000.00 或 目標價 NT$ 479.00
            price_match = re.search(r'(?:Price [Tt]arget|目標價).*?(?:NT\$|Target Price)?\s*([\d,.]+)', text, re.S)
            if price_match:
                data["目標價"] = price_match.group(1).replace(',', '')

    except Exception as e:
        print(f"解析 {file_path} 失敗: {e}")
        
    return data
