import pandas as pd
import os

base_path = r"c:\Users\56975\Desktop\presentacion integrados\proyecto\docs"
files = [
    "9 SEPTIEMBRE URNI (Autoguardado) - copia (2).xlsx",
    "LIBRO DE PARTOS 09 SEPTIEMBRE 2025 (Autoguardado) (1).xlsx"
]

for file in files:
    path = os.path.join(base_path, file)
    print(f"\n{'='*50}")
    print(f"ANALYZING: {file}")
    print(f"{'='*50}")
    
    try:
        xls = pd.ExcelFile(path)
        print(f"SHEETS: {xls.sheet_names}")
        
        for sheet in xls.sheet_names:
            print(f"\n--- SHEET: {sheet} ---")
            df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
            print("COLUMNS:")
            for col in df.columns:
                print(f"  - {col}")
            print("\nSAMPLE DATA (First 2 rows):")
            print(df.head(2).to_string())
            
    except Exception as e:
        print(f"ERROR reading file: {e}")
