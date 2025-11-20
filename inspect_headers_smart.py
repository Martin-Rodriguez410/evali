import pandas as pd
import os

base_path = r"c:\Users\56975\Desktop\presentacion integrados\proyecto\docs"
file_name = "LIBRO DE PARTOS 09 SEPTIEMBRE 2025 (Autoguardado) (1).xlsx"
path = os.path.join(base_path, file_name)

print(f"INSPECTING: {file_name}")

try:
    xls = pd.ExcelFile(path)
    sheet = xls.sheet_names[0] # Assume data is in the first sheet
    print(f"SHEET: {sheet}")
    
    df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=15)
    
    print("\nSEARCHING FOR HEADERS (Row by Row):")
    for i, row in df.iterrows():
        # Get non-null values in this row
        values = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip() != '']
        if values:
            print(f"ROW {i}: {values}")

except Exception as e:
    print(f"ERROR: {e}")
