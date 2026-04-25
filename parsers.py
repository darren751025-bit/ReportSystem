import pdfplumber
import re

def extract_financial_data(pdf_path):
    data = {
        "日期": "-", "代號": "-", "名稱": "-", "券商": "未知",
        "建議": "中立", "目標價": "-", "昨收": "-"
    }
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0].extract_text() or ""
            
            # 永豐投顧邏輯
            if "SinoPac" in first_page or "永豐" in first_page:
                data["券商"] = "永豐投顧"
                d_m = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", first_page)
                if d_m: data["日期"] = d_m.group(1)
                cn_m = re.search(r"(\w+)\s*\((\d{4})\s*TT\)", first_page)
                if cn_m: data["名稱"], data["代號"] = cn_m.groups()
                rec_m = re.search(r"投資建議\s*([\u4e00-\u9fa5]+)", first_page)
                if rec_m: data["建議"] = rec_m.group(1)
                tp_m = re.search(r"目標價\s*NT\$\s*([\d,.]+)", first_page)
                if tp_m: data["目標價"] = tp_m.group(1)
                ls_m = re.search(r"收盤價\s*NT\$\s*([\d,.]+)", first_page)
                if ls_m: data["昨收"] = ls_m.group(1)

            # 大摩邏輯
            elif "Morgan Stanley" in first_page:
                data["券商"] = "Morgan Stanley"
                ms_m = re.search(r"(.+?)\s*\((\d{4})\.TW", first_page)
                if ms_m: data["名稱"], data["代號"] = ms_m.groups()
                if "Overweight" in first_page: data["建議"] = "買進"
                elif "Underweight" in first_page: data["建議"] = "賣出"
                tp_m = re.search(r"Price [Tt]arget\s*NT\$([\d,.]+)", first_page)
                if tp_m: data["目標價"] = tp_m.group(1)
                ls_m = re.search(r"close \(.*?\)\s*NT\$([\d,.]+)", first_page)
                if ls_m: data["昨收"] = ls_m.group(1)
    except Exception as e:
        print(f"!!! 檔案 {pdf_path} 解析出錯: {e}")
    return data
