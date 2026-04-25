import pdfplumber
import os
from datetime import datetime
from pathlib import Path

def extract_financial_data(file_path):
    p = Path(file_path)
    # 自動抓取檔案修改時間作為日期
    file_date = datetime.fromtimestamp(p.stat().st_mtime).date()
    
    data = {
        "日期": file_date,
        "代號": "N/A",
        "名稱": p.name,
        "券商": "系統解析",
        "建議": "中立",
        "目標價": "-"
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            first_page_text = pdf.pages[0].extract_text()
            if first_page_text:
                # 簡單的券商識別邏輯
                if "永豐" in first_page_text: data["券商"] = "永豐投顧"
                elif "凱基" in first_page_text: data["券商"] = "凱基證券"
                elif "Morgan" in first_page_text: data["券商"] = "大摩"
    except Exception:
        pass 
        
    return data
