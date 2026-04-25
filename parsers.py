import pdfplumber
import datetime

def extract_financial_data(file_path):
    # 預設資料，加入當前日期作為預設值
    data = {
        "日期": datetime.date.today(), 
        "代號": "N/A",
        "名稱": "未命名報告",
        "券商": "未知券商",
        "建議": "中立",
        "目標價": "-"
    }
    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            if text:
                # 這裡僅模擬解析，實際開發可加入正規表達式
                data["名稱"] = f"已解析: {file_path.split('/')[-1]}"
    except Exception as e:
        print(f"解析錯誤: {e}")
    return data
