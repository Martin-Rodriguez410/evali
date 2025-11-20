import pandas as pd
import os

base_path = r"c:\Users\56975\Desktop\presentacion integrados\proyecto\docs"
file_name = "LIBRO DE PARTOS 09 SEPTIEMBRE 2025 (Autoguardado) (1).xlsx"
path = os.path.join(base_path, file_name)

keywords = ["NOMBRE", "RUT", "EDAD", "PARTO", "PESO", "TALLA", "APGAR", "FECHA"]

try:
    xls = pd.ExcelFile(path)
    sheet = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=20)
    
    best_row = -1
    max_matches = 0
    
    print(f"Scanning first 20 rows of '{sheet}' for headers...")
    
    for i, row in df.iterrows():
        matches = 0
        row_str = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
        
        for kw in keywords:
            if kw in row_str:
                matches += 1
        
        if matches > 0:
            print(f"Row {i} has {matches} matches: {row_str[:100]}...")
            
        if matches > max_matches:
            max_matches = matches
            best_row = i
            
    print(f"\nBEST GUESS: Header is at Row {best_row} with {max_matches} matches.")
    
    if best_row != -1:
        # Print the actual columns from that row
        print(f"COLUMNS found in Row {best_row}:")
        headers = df.iloc[best_row].values
        for idx, h in enumerate(headers):
            if pd.notna(h):
                print(f"  Col {idx}: {h}")

except Exception as e:
    print(f"ERROR: {e}")
