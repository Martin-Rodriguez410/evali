import os
import django
from django.conf import settings
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obstetricia.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ["DJANGO_DEBUG"] = "True"
django.setup()

from registros.models import Madre, Parto, RecienNacido
from registros.pdf_export import exportar_datos_pdf
from registros.excel_export import exportar_datos_excel
from registros.import_data import importar_datos_excel
from django.contrib.auth import get_user_model

def test_export_pdf():
    print("Testing PDF Export...")
    try:
        response = exportar_datos_pdf()
        if response.status_code == 200 and response['Content-Type'] == 'application/pdf':
            print("PDF Export: SUCCESS")
        else:
            print(f"PDF Export: FAILED (Status: {response.status_code}, Type: {response.get('Content-Type')})")
    except Exception as e:
        print(f"PDF Export: ERROR ({e})")

def test_export_excel():
    print("Testing Excel Export...")
    try:
        response = exportar_datos_excel()
        if response.status_code == 200 and response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            print("Excel Export: SUCCESS")
            return response.content
        else:
            print(f"Excel Export: FAILED (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"Excel Export: ERROR ({e})")
        return None

def test_import_excel(excel_content):
    print("Testing Import Excel...")
    if not excel_content:
        print("Skipping Import Test (No Excel content)")
        return

    from io import BytesIO
    file = BytesIO(excel_content)
    User = get_user_model()
    user = User.objects.first()
    if not user:
        print("Skipping Import Test (No user found)")
        return

    result = importar_datos_excel(file, user)
    if result['success']:
        print(f"Import Excel: SUCCESS (Counts: {result['counts']})")
    else:
        print(f"Import Excel: FAILED ({result.get('message')})")
        if result.get('errors'):
            print("Errors:", result['errors'][:5])

if __name__ == '__main__':
    test_export_pdf()
    excel_content = test_export_excel()
    # We can test import with the exported file to verify round-trip (mostly)
    # Note: This might duplicate data if not careful, but our logic handles updates.
    if excel_content:
        test_import_excel(excel_content)
