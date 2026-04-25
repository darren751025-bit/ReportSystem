import pdfplumber
from pathlib import Path
from datetime import datetime

def extract_financial_data(file_path):
    p = Path(file_path)
    # 取得檔案日期
    file_date = datetime.fromtimestamp(p.stat().st_mtime).date()
    
    data = {
        "日期": file_date,
        "代號": "N/A",
        "名稱": p.name,
        "券商": "未辨識",
        "建議": "持平",
        "目標價": "-"
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            first_page_text = pdf.pages[0].extract_text()
            if first_page_text:
                # 基礎偵測邏輯
                if "永豐" in first_page_text: data["券商"] = "永豐投顧"
                if "凱基" in first_page_text: data["券商"] = "凱基證券"
    except Exception:
        pass
    return data
