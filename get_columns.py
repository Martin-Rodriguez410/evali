import pandas as pd
import os

base_path = r"c:\Users\56975\Desktop\presentacion integrados\proyecto\docs"
file_name = "LIBRO DE PARTOS 09 SEPTIEMBRE 2025 (Autoguardado) (1).xlsx"
path = os.path.join(base_path, file_name)

try:
    xls = pd.ExcelFile(path)
    sheet = xls.sheet_names[0]
    # Read header from row 2 (0-indexed)
    df = pd.read_excel(xls, sheet_name=sheet, header=2, nrows=0) 
    
    print("COLUMNS_FOUND:")
    for col in df.columns:
        print(f"'{col}'")

except Exception as e:
    print(f"ERROR:{e}")
