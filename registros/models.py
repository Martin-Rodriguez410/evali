from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Madre(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('soltera', 'Soltera'),
        ('casada', 'Casada'),
        ('viuda', 'Viuda'),
        ('divorciada', 'Divorciada'),
        ('conviviente', 'Conviviente'),
    ]

    PREVISION_CHOICES = [
        ('fonasa_a', 'Fonasa A'),
        ('fonasa_b', 'Fonasa B'),
        ('fonasa_c', 'Fonasa C'),
        ('fonasa_d', 'Fonasa D'),
        ('isapre', 'Isapre'),
        ('particular', 'Particular'),
        ('prais', 'PRAIS'),
        ('otra', 'Otra'),
    ]

    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT", db_index=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    prevision = models.CharField(max_length=20, choices=PREVISION_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='madres_creadas'
    )

    def clean(self):
        # Normalize rut first
        try:
            from .utils import normalize_rut, format_rut
            norm = normalize_rut(self.rut)
            if norm:
                self.rut = format_rut(norm)
        except Exception:
            pass
        from django.core.exceptions import ValidationError
        from datetime import date
        import re

        # Validar edad mínima y máxima
        if self.fecha_nacimiento:
            edad = (date.today() - self.fecha_nacimiento).days // 365
            if edad < 12:
                raise ValidationError('La paciente debe tener al menos 12 años.')
            if edad > 60:
                raise ValidationError('Por favor, verifique la fecha de nacimiento.')


        # Validar dígito verificador del RUT
        # Primero validar que el RUT no esté vacío
        if not self.rut or not self.rut.strip():
            raise ValidationError('El RUT es requerido.')

        rut_limpio = self.rut.replace('.', '').replace('-', '').strip()

        # Validar que el RUT tenga contenido después de limpiar
        if not rut_limpio or len(rut_limpio) < 2:
            raise ValidationError('El RUT ingresado no es válido. Debe tener el formato: 12345678-9')

        # Extraer dígito verificador y número de forma segura
        try:
            dv = rut_limpio[-1].upper()
            rut_numero = int(rut_limpio[:-1])
        except (IndexError, ValueError):
            raise ValidationError('El RUT contiene caracteres inválidos. Use el formato: 12345678-9')

        # Validar que el dígito verificador sea válido (0-9 o K)
        if dv not in '0123456789K':
            raise ValidationError('El dígito verificador debe ser un número (0-9) o la letra K.')

        # Validar que el número del RUT sea válido
        if rut_numero <= 0:
            raise ValidationError('El RUT debe ser un número válido mayor a 0.')

        calculated_dv = self.calcular_dv(rut_numero)
        if dv != calculated_dv:
            raise ValidationError('El RUT ingresado no es válido.')

        # Validar formato del teléfono: aceptar varios formatos comunes (+56 9 9xxxxxxxx, 9xxxxxxxx, with spaces/dashes)
        if self.telefono:
            if not re.match(r'^[0-9\+\s\-()]{7,20}$', self.telefono):
                raise ValidationError('El formato del teléfono parece inválido. Use +56 9 XXXXXXXX o formato local.')

    @staticmethod
    def calcular_dv(rut):
        multiplicador = 2
        suma = 0
        while rut > 0:
            suma += (rut % 10) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
            rut //= 10
        resto = suma % 11
        if resto == 0:
            return 'K'
        elif resto == 1:
            return '0'
        else:
            return str(11 - resto)

    @property
    def edad(self):
        from datetime import date
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.rut}"

    class Meta:
        verbose_name = "Madre"
        verbose_name_plural = "Madres"

class Parto(models.Model):
    TIPO_PARTO_CHOICES = [
        ('cesarea_urgencia', 'Cesárea Urgencia'),
        ('cesarea_electiva', 'Cesárea Electiva'),
        ('distocico', 'Distocico'),
        ('eutocico', 'Eutocico'),
    ]

    TIPO_ANESTESIA_CHOICES = [
        ('ninguna', 'Ninguna'),
        ('local', 'Local'),
        ('epidural', 'Epidural'),
        ('raquidea', 'Raquídea'),
        ('general', 'General'),
    ]

    CLASIFICACION_ROBSON_CHOICES = [
        ('grupo_1', 'Grupo 1'),
        ('grupo_2a', 'Grupo 2A'),
        ('grupo_2b', 'Grupo 2B'),
        ('grupo_3', 'Grupo 3'),
        ('grupo_4a', 'Grupo 4A'),
        ('grupo_4b', 'Grupo 4B'),
        ('grupo_5a', 'Grupo 5A'),
        ('grupo_5b', 'Grupo 5B'),
        ('grupo_6', 'Grupo 6'),
        ('grupo_7', 'Grupo 7'),
        ('grupo_8', 'Grupo 8'),
        ('grupo_10', 'Grupo 10'),
    ]

    PERSONA_ACOMPANANTE_CHOICES = [
        ('pareja', 'Pareja'),
        ('hermano', 'Hermana/o'),
        ('padre_madre', 'Padre/Madre'),
        ('tio', 'Tía/o'),
        ('suegro', 'Suegra/o'),
    ]

    madre = models.ForeignKey(Madre, on_delete=models.CASCADE, related_name='partos')
    fecha_hora = models.DateTimeField(db_index=True)
    
    # Campos para "Trabajo de Parto"
    paridad = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name="Paridad"
    )
    semanas_obstetricas = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Semanas Obstétricas"
    )
    semanas_obstetricas_dias = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Semanas Obstétricas (días)"
    )
    monitor = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Monitor"
    )
    ttc = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="TTC"
    )
    induccion = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Inducción"
    )
    tipo_parto = models.CharField(
        max_length=20,
        choices=TIPO_PARTO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Tipo de Parto"
    )
    alumbramiento_dirigido = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Alumbramiento dirigido"
    )
    clasificacion_robson = models.CharField(
        max_length=20,
        choices=CLASIFICACION_ROBSON_CHOICES,
        null=True,
        blank=True,
        verbose_name="Clasificación de Robson"
    )
    acompanamiento_parto = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Acompañamiento Parto"
    )
    motivo_parto_no_acompanado = models.TextField(
        blank=True,
        verbose_name="Motivo Parto NO acompañado"
    )
    persona_acompanante = models.CharField(
        max_length=20,
        choices=PERSONA_ACOMPANANTE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Persona Acompañante"
    )
    acompanante_secciona_cordon = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Acompañante secciona cordón"
    )
    
    # Campos para "Información de los profesionales"
    profesional_a_cargo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Profesional a cargo"
    )
    causa_cesarea = models.TextField(
        blank=True,
        verbose_name="Causa cesárea"
    )
    
    # Campos para "Otros registros"
    uso_sala_saip = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Uso sala SAIP"
    )
    ley_21372_dominga = models.TextField(
        blank=True,
        verbose_name="Ley N° 21.372 Dominga",
        help_text="Cuales recuerdos (de no entregar justificar motivo)"
    )
    retira_placenta = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Retira placenta"
    )
    estampado_placenta = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Estampado de placenta"
    )
    folio_valido = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Folio válido"
    )
    folios_nulos = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Folio/s Nulo/s"
    )
    manejo_dolor_no_farmacologico = models.TextField(
        blank=True,
        verbose_name="Manejo del dolor no farmacológico"
    )
    
    # Campos antiguos mantenidos como opcionales para compatibilidad
    semanas_gestacion = models.IntegerField(
        validators=[MinValueValidator(20), MaxValueValidator(45)],
        null=True,
        blank=True
    )
    tipo_anestesia = models.CharField(max_length=20, choices=TIPO_ANESTESIA_CHOICES, null=True, blank=True)
    complicaciones = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='partos_registrados'
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import timedelta
        from django.utils import timezone

        # Validar que la fecha no sea futura (use timezone-aware now)
        now = timezone.now()
        if self.fecha_hora and self.fecha_hora > now:
            raise ValidationError('La fecha y hora no puede ser futura.')

        # Validar que la fecha no sea anterior a 48 horas
        # Allow bypass when instance has been flagged (e.g., via a form wrapper)
        allow_old = getattr(self, '_allow_old_parto', False)
        if not allow_old and self.fecha_hora and self.fecha_hora < now - timedelta(hours=48):
            raise ValidationError('No se pueden registrar partos con más de 48 horas de antigüedad.')

        # Validar edad gestacional (solo si está presente)
        if self.semanas_gestacion is not None:
            if self.semanas_gestacion < 20:
                raise ValidationError('La edad gestacional no puede ser menor a 20 semanas.')
            if self.semanas_gestacion > 45:
                raise ValidationError('La edad gestacional no puede ser mayor a 45 semanas.')

    def save(self, *args, **kwargs):
        # Registrar usuario que crea/modifica el registro
        if not self.pk and not self.created_by:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.created_by = User.get_current_user() if hasattr(User, 'get_current_user') else None
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Parto de {self.madre} - {self.fecha_hora.date()}"

    class Meta:
        verbose_name = "Parto"
        verbose_name_plural = "Partos"
        ordering = ['-fecha_hora']  # Ordenar por fecha descendente

class RecienNacido(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    ESTADO_CHOICES = [
        ('vivo', 'Vivo'),
        ('fallecido', 'Fallecido'),
    ]

    parto = models.ForeignKey(Parto, on_delete=models.CASCADE, related_name='recien_nacidos')
    hora_nacimiento = models.TimeField(db_index=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0.1), MaxValueValidator(6.0)]
    )
    talla = models.DecimalField(
        max_digits=4,
        decimal_places=1
    )
    apgar_1 = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    apgar_5 = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='vivo')
    observaciones = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import datetime, timedelta
        import logging
        logger = logging.getLogger(__name__)
        # Validar hora de nacimiento con respecto a la hora del parto
        # Use parto_id to avoid accessing related descriptor when FK not assigned yet
        parto_obj = None
        if getattr(self, 'parto_id', None):
            try:
                parto_obj = Parto.objects.get(pk=self.parto_id)
            except Parto.DoesNotExist:
                parto_obj = None

        # If there's a provisional parto datetime attached (from combined form), prefer it
        provisional_dt = getattr(self, '_parto_fecha_hora', None)
        if provisional_dt and self.hora_nacimiento:
            # Build datetimes on the same date to compute an accurate seconds delta
            try:
                nacimiento_dt = datetime.combine(provisional_dt.date(), self.hora_nacimiento)
                if provisional_dt.tzinfo is not None:
                    # preserve timezone awareness
                    nacimiento_dt = nacimiento_dt.replace(tzinfo=provisional_dt.tzinfo)
                delta_seconds = abs((nacimiento_dt - provisional_dt).total_seconds())
                logger.info('RecienNacido.clean provisional compare: parto=%s nacimiento=%s delta_seconds=%s',
                            provisional_dt.isoformat(), getattr(nacimiento_dt, 'isoformat', lambda: str(nacimiento_dt))(), delta_seconds)
                if delta_seconds > 5400:  # more than 90 minutes
                    raise ValidationError('La hora de nacimiento no puede diferir en más de 1 hora de la hora del parto.')
            except TypeError:
                # Fallback to previous minutes granularity if types mismatch
                hora_parto = provisional_dt.time()
                minutos_parto = hora_parto.hour * 60 + hora_parto.minute
                minutos_nacimiento = self.hora_nacimiento.hour * 60 + self.hora_nacimiento.minute
                if abs(minutos_nacimiento - minutos_parto) > 60:
                    raise ValidationError('La hora de nacimiento no puede diferir en más de 1 hora de la hora del parto.')

        if parto_obj and self.hora_nacimiento:
            try:
                parto_dt = parto_obj.fecha_hora
                nacimiento_dt = datetime.combine(parto_dt.date(), self.hora_nacimiento)
                if parto_dt.tzinfo is not None:
                    nacimiento_dt = nacimiento_dt.replace(tzinfo=parto_dt.tzinfo)
                delta_seconds = abs((nacimiento_dt - parto_dt).total_seconds())
                logger.info('RecienNacido.clean compare: parto=%s nacimiento=%s delta_seconds=%s',
                            parto_dt.isoformat(), getattr(nacimiento_dt, 'isoformat', lambda: str(nacimiento_dt))(), delta_seconds)
                if delta_seconds > 5400:
                    raise ValidationError('La hora de nacimiento no puede diferir en más de 1 hora de la hora del parto.')
            except TypeError:
                hora_parto = parto_obj.fecha_hora.time()
                # Convertir a minutos para comparar
                minutos_parto = hora_parto.hour * 60 + hora_parto.minute
                minutos_nacimiento = self.hora_nacimiento.hour * 60 + self.hora_nacimiento.minute
                if abs(minutos_nacimiento - minutos_parto) > 60:
                    raise ValidationError('La hora de nacimiento no puede diferir en más de 1 hora de la hora del parto.')

        # Validar peso según edad gestacional
        # Preferir semanas desde el objeto parto si existe, sino usar la provisional adjuntada por el formulario combinado
        semanas = None
        if parto_obj and getattr(parto_obj, 'semanas_gestacion', None) is not None:
            semanas = parto_obj.semanas_gestacion
        else:
            semanas = getattr(self, '_parto_semanas', None)

        if self.peso and semanas:
            peso_min = 0.3  # 300g
            if semanas >= 37:  # A término
                if self.peso < 2.0:  # 2000g
                    raise ValidationError('El peso es muy bajo para un bebé a término.')
                if self.peso > 5.0:  # 5000g
                    raise ValidationError('El peso es muy alto, por favor verificar.')
            else:  # Pretérmino
                if self.peso < peso_min:
                    raise ValidationError(f'El peso no puede ser menor a {peso_min}kg.')
                if self.peso > 4.0:  # 4000g
                    raise ValidationError('El peso es muy alto para un bebé pretérmino.')

        # Validar APGAR
        if self.apgar_1 is not None and self.apgar_5 is not None:
            if self.apgar_5 < self.apgar_1:
                raise ValidationError('El APGAR a los 5 minutos no puede ser menor que el APGAR al minuto.')
            if self.apgar_1 == 0 and self.estado == 'vivo':
                raise ValidationError('Un APGAR de 0 al minuto no es compatible con estado "vivo".')

    def save(self, *args, **kwargs):
        # Calcular riesgo basado en APGAR
        if self.apgar_1 is not None:
            if self.apgar_1 <= 3:
                self.riesgo = 'alto'
            elif self.apgar_1 <= 6:
                self.riesgo = 'medio'
            else:
                self.riesgo = 'bajo'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"RN de {self.parto.madre} - {self.hora_nacimiento}"

    class Meta:
        verbose_name = "Recién Nacido"
        verbose_name_plural = "Recién Nacidos"

class SesionUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Sesión de {self.usuario.username} - {self.fecha_inicio}"

    class Meta:
        verbose_name = "Sesión de Usuario"
        verbose_name_plural = "Sesiones de Usuario"
