import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obstetricia.settings')
django.setup()

from registros.import_data import importar_datos_excel

base_path = r"c:\Users\56975\Desktop\presentacion integrados\proyecto\docs"
file_name = "LIBRO DE PARTOS 09 SEPTIEMBRE 2025 (Autoguardado) (1).xlsx"
file_path = os.path.join(base_path, file_name)

print(f"TESTING IMPORT WITH: {file_name}")

try:
    with open(file_path, 'rb') as f:
        # Create a mock uploaded file
        uploaded_file = SimpleUploadedFile(file_name, f.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        stats = importar_datos_excel(uploaded_file)
        
        print("\nIMPORT RESULTS:")
        print(f"Created: {stats['created']}")
        print(f"Updated: {stats['updated']}")
        print(f"Errors: {len(stats['errors'])}")
        
        if stats['errors']:
            print("\nFIRST 5 ERRORS:")
            for err in stats['errors'][:5]:
                print(f" - {err}")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
