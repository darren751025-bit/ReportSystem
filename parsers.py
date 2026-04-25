import pdfplumber
import re

def extract_financial_data(pdf_path):
    data = {
        "日期": "", "代號": "", "名稱": "", "券商": "未知券商",
        "建議": "未偵測", "目標價": "-", "昨收": "-"
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0].extract_text()
        full_text = "".join([p.extract_text() for p in pdf.pages])
        
        # 1. 判斷券商並抓取資訊
        if "SinoPac" in full_text or "永豐" in full_text:
            data["券商"] = "永豐投顧"
            # 抓取日期 (格式: 2026/3/12)
            date_match = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", first_page)
            if date_match: data["日期"] = date_match.group(1)
            
            # 抓取代號名稱 (格式: M31 (6643 TT))
            code_name = re.search(r"(\w+)\s*\((\d{4})\s*TT\)", first_page)
            if code_name:
                data["名稱"], data["代號"] = code_name.groups()
                
            # 抓取投資建議
            rec_match = re.search(r"投資建議\s*([\u4e00-\u9fa5]+)", first_page)
            if rec_match: data["建議"] = rec_match.group(1)
            
            # 抓取目標價與昨收
            target_match = re.search(r"6個月目標價\s*NT\$\s*([\d,.]+)", first_page)
            if target_match: data["目標價"] = target_match.group(1)
            last_match = re.search(r"收盤價\s*NT\$\s*([\d,.]+)", first_page)
            if last_match: data["昨收"] = last_match.group(1)

        elif "Morgan Stanley" in full_text:
            data["券商"] = "Morgan Stanley"
            # 抓取名稱與代號 (格式: Gold Circuit Electronics Ltd. (2368.TW))
            ms_info = re.search(r"(.+?)\s*\((\d{4})\.TW", first_page)
            if ms_info:
                data["名稱"], data["代號"] = ms_info.groups()
            
            # 抓取日期
            date_match = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", first_page)
            if date_match: data["日期"] = date_match.group(1)

            # 抓取投資建議 (外資術語轉換)
            if "Overweight" in first_page: data["建議"] = "買進 (加碼)"
            elif "Equal-weight" in first_page: data["建議"] = "持有 (中立)"
            elif "Underweight" in first_page: data["建議"] = "賣出 (減持)"
            
            # 抓取目標價
            target_match = re.search(r"Price target\s*NT\$([\d,.]+)", first_page)
            if target_match: data["目標價"] = target_match.group(1)
            # 抓取昨收
            last_match = re.search(r"close \(.*?\)\s*NT\$([\d,.]+)", first_page)
            if last_match: data["昨收"] = last_match.group(1)

    return data
