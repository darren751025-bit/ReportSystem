import pdfplumber
import re

def extract_financial_data(pdf_path):
    # 預設資料
    data = {
        "日期": "-", "代號": "-", "名稱": "-", "券商": "偵測中",
        "建議": "中立", "目標價": "-", "昨收": "-"
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0].extract_text() or ""
            
            # --- 1. 永豐投顧 (SinoPac) 邏輯 ---
            if "永豐" in first_page or "SinoPac" in first_page:
                data["券商"] = "永豐投顧"
                # 日期 (YYYY/MM/DD)
                d_m = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", first_page)
                if d_m: data["日期"] = d_m.group(1)
                # 代號名稱 (例如: M31 (6643 TT))
                cn_m = re.search(r"(\w+)\s*\((\d{4})\s*TT\)", first_page)
                if cn_m:
                    data["名稱"], data["代號"] = cn_m.groups()
                # 建議
                rec_m = re.search(r"投資建議\s*([\u4e00-\u9fa5]+)", first_page)
                if rec_m: data["建議"] = rec_m.group(1)
                # 目標價
                tp_m = re.search(r"目標價\s*NT\$\s*([\d,.]+)", first_page)
                if tp_m: data["目標價"] = tp_m.group(1)

            # --- 2. 大摩 (Morgan Stanley) 邏輯 ---
            elif "Morgan Stanley" in first_page:
                data["券商"] = "大摩 (MS)"
                # 代號名稱 (例如: 2368.TW)
                ms_m = re.search(r"(.+?)\s*\((\d{4})\.TW", first_page)
                if ms_m:
                    data["名稱"], data["代號"] = ms_m.groups()
                # 建議
                if "Overweight" in first_page: data["建議"] = "買進"
                elif "Equal-weight" in first_page: data["建議"] = "持有"
                elif "Underweight" in first_page: data["建議"] = "賣出"
                # 目標價
                tp_m = re.search(r"Price [Tt]arget\s*NT\$([\d,.]+)", first_page)
                if tp_m: data["目標價"] = tp_m.group(1)

    except Exception as e:
        print(f"解析失敗: {pdf_path}, 錯誤: {e}")
        
    return data
