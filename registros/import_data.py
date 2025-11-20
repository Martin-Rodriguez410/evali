import pandas as pd
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Madre, Parto, RecienNacido
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def normalize_col(name):
    """Normaliza el nombre de la columna para facilitar el matching."""
    if not isinstance(name, str):
        return str(name)
    return name.upper().strip().replace('\n', ' ').replace('.', '')

def find_col(columns, keywords):
    """Busca una columna que contenga alguna de las palabras clave."""
    for col in columns:
        norm = normalize_col(col)
        for kw in keywords:
            if kw in norm:
                return col
    return None

def importar_datos_excel(file, user=None):
    try:
        # Intentar detectar la fila de cabecera automáticamente
        # Leemos las primeras 10 filas para buscar palabras clave
        xls = pd.ExcelFile(file)
        df_preview = pd.read_excel(xls, nrows=10, header=None)
        
        header_row = 0
        max_matches = 0
        keywords_detect = ["NOMBRE", "RUT", "EDAD", "PARTO", "PESO"]
        
        for i, row in df_preview.iterrows():
            matches = 0
            row_str = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
            for kw in keywords_detect:
                if kw in row_str:
                    matches += 1
            if matches > max_matches:
                max_matches = matches
                header_row = i
        
        # Leer el archivo con la cabecera detectada
        df = pd.read_excel(file, header=header_row)
        
        # Normalizar columnas del DF para búsqueda
        original_cols = df.columns
        df.columns = [normalize_col(c) for c in df.columns]
        cols = df.columns
        
        # Mapeo de columnas (Búsqueda flexible)
        col_rut = find_col(cols, ["RUT", "IDENTIFICACION"])
        col_nombre = find_col(cols, ["NOMBRE", "PACIENTE"])
        col_edad = find_col(cols, ["EDAD"])
        col_fecha = find_col(cols, ["FECHA"])
        col_hora = find_col(cols, ["HORA"])
        col_comuna = find_col(cols, ["COMUNA", "PROCEDENCIA"])
        col_prevision = find_col(cols, ["PREVISION"])
        col_tipo_parto = find_col(cols, ["TIPO DE PARTO", "VIA DE PARTO"])
        col_sexo = find_col(cols, ["SEXO", "GENERO"])
        col_peso = find_col(cols, ["PESO"])
        col_talla = find_col(cols, ["TALLA"])
        col_apgar1 = find_col(cols, ["APGAR 1", "APGAR 1 MIN"])
        col_apgar5 = find_col(cols, ["APGAR 5", "APGAR 5 MIN"])
        
        stats = {'created': 0, 'updated': 0, 'errors': []}
        
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # 1. Procesar Madre
                    rut_raw = str(row.get(col_rut, '')).strip() if col_rut else ''
                    if not rut_raw or rut_raw.lower() == 'nan':
                        continue # Saltar filas vacías
                        
                    # Limpieza básica de RUT
                    rut_clean = rut_raw.replace('.', '').replace(' ', '').upper()
                    if '-' not in rut_clean and len(rut_clean) > 1:
                        rut_clean = f"{rut_clean[:-1]}-{rut_clean[-1]}"
                    
                    nombre_completo = str(row.get(col_nombre, 'Desconocida')).strip()
                    # Intentar separar nombre y apellido
                    parts = nombre_completo.split()
                    if len(parts) >= 2:
                        nombres = " ".join(parts[:len(parts)//2])
                        apellidos = " ".join(parts[len(parts)//2:])
                    else:
                        nombres = nombre_completo
                        apellidos = "."
                        
                    # Calcular fecha nacimiento aproximada si solo hay edad
                    edad = row.get(col_edad)
                    fecha_nacimiento = None
                    if edad and pd.notna(edad):
                        try:
                            edad_int = int(float(edad))
                            year_nac = datetime.now().year - edad_int
                            fecha_nacimiento = datetime(year_nac, 1, 1).date()
                        except:
                            pass
                    
                    if not fecha_nacimiento:
                        fecha_nacimiento = datetime(2000, 1, 1).date() # Default
                        
                    madre, created = Madre.objects.update_or_create(
                        rut=rut_clean,
                        defaults={
                            'nombres': nombres,
                            'apellidos': apellidos,
                            'fecha_nacimiento': fecha_nacimiento,
                            'comuna': str(row.get(col_comuna, '')),
                            'prevision': 'fonasa_a', # Default simple
                            'estado_civil': 'soltera',
                            'created_by': user if user and user.is_authenticated else None
                        }
                    )
                    
                    # 2. Procesar Parto
                    fecha_raw = row.get(col_fecha)
                    hora_raw = row.get(col_hora)
                    
                    fecha_parto = timezone.now()
                    if pd.notna(fecha_raw):
                        try:
                            if isinstance(fecha_raw, datetime):
                                fecha_parto = fecha_raw
                            else:
                                # Intentar parsear string
                                fecha_parto = pd.to_datetime(fecha_raw).to_pydatetime()
                        except:
                            pass
                            
                    # Combinar con hora si existe
                    if pd.notna(hora_raw):
                        try:
                            if isinstance(hora_raw, datetime): # A veces pandas lee hora como datetime
                                hora_time = hora_raw.time()
                            else:
                                hora_time = pd.to_datetime(str(hora_raw), format='%H:%M:%S').time()
                            
                            fecha_parto = fecha_parto.replace(
                                hour=hora_time.hour, 
                                minute=hora_time.minute, 
                                second=hora_time.second
                            )
                        except:
                            pass
                            
                    # Mapeo tipo parto
                    tipo_parto_raw = str(row.get(col_tipo_parto, '')).upper()
                    tipo_parto = 'vaginal'
                    if 'CESAREA' in tipo_parto_raw or 'CESÁREA' in tipo_parto_raw:
                        tipo_parto = 'cesarea'
                    elif 'FORCEPS' in tipo_parto_raw:
                        tipo_parto = 'forceps'
                        
                    parto, p_created = Parto.objects.update_or_create(
                        madre=madre,
                        fecha_hora=fecha_parto,
                        defaults={
                            'tipo_parto': tipo_parto,
                            'semanas_gestacion': 39, # Default si no hay dato
                            'tipo_anestesia': 'ninguna',
                            '_allow_old_parto': True, # Bypass validación 48h
                            'created_by': user if user and user.is_authenticated else None
                        }
                    )
                    
                    # 3. Procesar Recién Nacido
                    sexo_raw = str(row.get(col_sexo, '')).upper()
                    sexo = 'M' if 'M' in sexo_raw or 'HOMBRE' in sexo_raw else 'F'
                    
                    peso = row.get(col_peso)
                    try:
                        peso = float(peso)
                        if peso > 100: # Probablemente en gramos
                            peso = peso / 1000.0
                    except:
                        peso = 3.0 # Default
                        
                    talla = row.get(col_talla)
                    try:
                        talla = float(talla)
                    except:
                        talla = 50.0
                        
                    RecienNacido.objects.update_or_create(
                        parto=parto,
                        defaults={
                            'hora_nacimiento': fecha_parto.time(),
                            'sexo': sexo,
                            'peso': peso,
                            'talla': talla,
                            'apgar_1': int(row.get(col_apgar1, 9)) if pd.notna(row.get(col_apgar1)) else 9,
                            'apgar_5': int(row.get(col_apgar5, 10)) if pd.notna(row.get(col_apgar5)) else 10,
                            'estado': 'vivo'
                        }
                    )
                    
                    if created or p_created:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                        
                except Exception as e:
                    stats['errors'].append(f"Fila {index}: {str(e)}")
                    
        return {
            'success': True,
            'counts': {
                'madres': stats['created'], # Simplificación: usamos created para todo
                'partos': stats['created'],
                'rn': stats['created']
            },
            'errors': stats['errors']
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error procesando el archivo: {str(e)}',
            'errors': [str(e)]
        }
