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

def parse_datetime_smart(date_val, time_val=None):
    """Intenta parsear fecha y hora de varias fuentes."""
    fecha_dt = timezone.now()
    
    # 1. Intentar parsear fecha
    if pd.notna(date_val):
        try:
            if isinstance(date_val, datetime):
                fecha_dt = date_val
            else:
                # Intentar formatos comunes
                str_val = str(date_val).strip()
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']:
                    try:
                        fecha_dt = datetime.strptime(str_val, fmt)
                        break
                    except:
                        continue
        except:
            pass

    # 2. Intentar parsear hora y combinar
    if pd.notna(time_val):
        try:
            time_obj = None
            if isinstance(time_val, datetime):
                time_obj = time_val.time()
            else:
                str_val = str(time_val).strip()
                # Intentar limpiar "hrs" o similares
                str_val = str_val.lower().replace('hrs', '').replace('hr', '').strip()
                for fmt in ['%H:%M:%S', '%H:%M', '%H']:
                    try:
                        time_obj = datetime.strptime(str_val, fmt).time()
                        break
                    except:
                        continue
            
            if time_obj:
                fecha_dt = fecha_dt.replace(
                    hour=time_obj.hour,
                    minute=time_obj.minute,
                    second=time_obj.second
                )
        except:
            pass
            
    return fecha_dt

def importar_datos_excel(file, user=None, import_type='auto'):
    try:
        # Detectar cabecera automáticamente
        xls = pd.ExcelFile(file)
        df_preview = pd.read_excel(xls, nrows=20, header=None)
        
        header_row = 0
        max_matches = 0
        # Palabras clave ampliadas para detectar mejor la cabecera
        keywords_detect = ["NOMBRE", "RUT", "EDAD", "PARTO", "PESO", "FECHA", "HORA", "MATRONA", "DIAGNOSTICO"]
        
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
        
        # Normalizar columnas
        df.columns = [normalize_col(c) for c in df.columns]
        cols = df.columns
        
        # Mapeo de columnas (Búsqueda flexible y ampliada)
        col_rut = find_col(cols, ["RUT", "IDENTIFICACION", "RUN"])
        col_nombre = find_col(cols, ["NOMBRE COMPLETO", "NOMBRE PACIENTE", "PACIENTE", "NOMBRE"])
        col_edad = find_col(cols, ["EDAD"])
        col_fecha = find_col(cols, ["FECHA PARTO", "FECHA DE PARTO", "FECHA"])
        col_hora = find_col(cols, ["HORA PARTO", "HORA DE PARTO", "HORA"])
        col_comuna = find_col(cols, ["COMUNA", "PROCEDENCIA", "DOMICILIO"])
        col_prevision = find_col(cols, ["PREVISION", "FINANCIADOR"])
        col_tipo_parto = find_col(cols, ["TIPO DE PARTO", "VIA DE PARTO", "TIPO PARTO"])
        col_sexo = find_col(cols, ["SEXO", "GENERO", "SEXO RN"])
        col_peso = find_col(cols, ["PESO", "PESO RN"])
        col_talla = find_col(cols, ["TALLA", "TALLA RN"])
        col_apgar1 = find_col(cols, ["APGAR 1", "APGAR 1 MIN", "APGAR 1'"])
        col_apgar5 = find_col(cols, ["APGAR 5", "APGAR 5 MIN", "APGAR 5'"])
        col_semanas = find_col(cols, ["EG", "EDAD GESTACIONAL", "SEMANAS"])
        
        stats = {'created': 0, 'updated': 0, 'errors': []}
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    # --- 1. Procesar Madre ---
                    rut_raw = str(row.get(col_rut, '')).strip() if col_rut else ''
                    if not rut_raw or rut_raw.lower() in ['nan', 'nat', 'none', '']:
                        continue # Saltar filas sin RUT
                        
                    # Limpieza de RUT
                    rut_clean = rut_raw.replace('.', '').replace(' ', '').upper()
                    if '-' not in rut_clean and len(rut_clean) > 1:
                        # Intentar formatear si viene sin guión
                        rut_clean = f"{rut_clean[:-1]}-{rut_clean[-1]}"
                    
                    nombre_completo = str(row.get(col_nombre, 'Desconocida')).strip()
                    if nombre_completo.lower() in ['nan', 'nat']: nombre_completo = 'Desconocida'
                    
                    # Separar nombre y apellido
                    parts = nombre_completo.split()
                    if len(parts) >= 2:
                        nombres = " ".join(parts[:len(parts)//2])
                        apellidos = " ".join(parts[len(parts)//2:])
                    else:
                        nombres = nombre_completo
                        apellidos = "."
                        
                    # Fecha nacimiento desde edad
                    edad = row.get(col_edad)
                    fecha_nacimiento = None
                    if pd.notna(edad):
                        try:
                            edad_int = int(float(edad))
                            year_nac = datetime.now().year - edad_int
                            fecha_nacimiento = datetime(year_nac, 1, 1).date()
                        except:
                            pass
                    
                    if not fecha_nacimiento:
                        fecha_nacimiento = datetime(2000, 1, 1).date()
                        
                    madre, created = Madre.objects.update_or_create(
                        rut=rut_clean,
                        defaults={
                            'nombres': nombres,
                            'apellidos': apellidos,
                            'fecha_nacimiento': fecha_nacimiento,
                            'comuna': str(row.get(col_comuna, ''))[:100],
                            'prevision': 'fonasa_a', # Default
                            'estado_civil': 'soltera',
                            'created_by': user if user and user.is_authenticated else None
                        }
                    )
                    
                    # --- 2. Procesar Parto ---
                    fecha_val = row.get(col_fecha)
                    hora_val = row.get(col_hora)
                    fecha_parto = parse_datetime_smart(fecha_val, hora_val)
                            
                    # Tipo parto
                    tipo_parto_raw = str(row.get(col_tipo_parto, '')).upper()
                    tipo_parto = 'vaginal'
                    if 'CESAREA' in tipo_parto_raw or 'CESÁREA' in tipo_parto_raw:
                        tipo_parto = 'cesarea'
                    elif 'FORCEPS' in tipo_parto_raw or 'FÓRCEPS' in tipo_parto_raw:
                        tipo_parto = 'forceps'
                        
                    # Semanas
                    semanas = 39
                    try:
                        eg_val = row.get(col_semanas)
                        if pd.notna(eg_val):
                            semanas = int(float(eg_val))
                    except:
                        pass
                        
                    parto, p_created = Parto.objects.update_or_create(
                        madre=madre,
                        fecha_hora=fecha_parto,
                        defaults={
                            'tipo_parto': tipo_parto,
                            'semanas_gestacion': semanas,
                            'tipo_anestesia': 'ninguna',
                            '_allow_old_parto': True, # Permitir históricos
                            'created_by': user if user and user.is_authenticated else None
                        }
                    )
                    
                    # --- 3. Procesar Recién Nacido ---
                    sexo_raw = str(row.get(col_sexo, '')).upper()
                    sexo = 'M'
                    if 'F' in sexo_raw or 'MUJER' in sexo_raw or 'FEMENINO' in sexo_raw:
                        sexo = 'F'
                    
                    peso = row.get(col_peso)
                    try:
                        peso = float(peso)
                        if peso > 100: # Gramos a kg
                            peso = peso / 1000.0
                    except:
                        peso = 3.0
                        
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
                stats['errors'].append(f"Fila {index + header_row + 2}: {str(e)}")
                    
        return {
            'success': True,
            'counts': {
                'madres': stats['created'], 
                'partos': stats['created'],
                'rn': stats['created']
            },
            'errors': stats['errors'][:20] # Limitar errores retornados
        }
        
    except Exception as e:
        logger.exception("Error importando excel")
        return {
            'success': False,
            'message': f'Error procesando el archivo: {str(e)}',
            'errors': [str(e)]
        }
