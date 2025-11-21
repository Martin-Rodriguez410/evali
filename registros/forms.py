import re
from django import forms
from django.core.validators import RegexValidator
from .models import Madre, Parto, RecienNacido

class MadreFormSimple(forms.ModelForm):
    """Formulario simplificado para crear madres desde la lista"""
    rut = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9 (sin puntos)',
            'pattern': r'^\d{7,8}-[\dkK]$'
        }),
        help_text='12.345.678-9'
    )
    
    fecha_nacimiento = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'dd-mm-aaaa',
            'pattern': r'^\d{2}-\d{2}-\d{4}$'
        }),
        input_formats=['%d-%m-%Y'],
        help_text='dd-mm-aaaa'
    )
    
    telefono = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+569XXXXXXXX',
            'pattern': r'^\+569\d{8}$'
        }),
        help_text='+56912345678)'
    )
    
    def clean_rut(self):
        from .utils import normalize_rut, format_rut, validate_rut
        import re
        raw = self.cleaned_data.get('rut', '').strip()
        
        # Aceptar formato sin puntos: 12345678-9
        if re.match(r'^\d{7,8}-[\dkK]$', raw):
            clean = raw.replace('-', '').upper()
            if validate_rut(clean):
                # Formatear a formato estándar con puntos
                formatted = format_rut(clean)
                # Verificar si ya existe
                if Madre.objects.filter(rut=formatted).exists():
                    raise forms.ValidationError('Ya existe una madre con ese RUT.')
                return formatted
            else:
                raise forms.ValidationError('El dígito verificador no es válido.')
        
        raise forms.ValidationError('El formato del RUT debe ser 12345678-9 (sin puntos, solo guion)')
    
    def clean_telefono(self):
        import re
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            # Validar formato +569XXXXXXXX
            if not re.match(r'^\+569\d{8}$', telefono):
                raise forms.ValidationError('El formato del teléfono debe ser +569XXXXXXXX (ej: +56912345678)')
        return telefono
    
    class Meta:
        model = Madre
        fields = ['rut', 'nombres', 'apellidos', 'fecha_nacimiento', 
                 'estado_civil', 'direccion', 'telefono', 'prevision']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'prevision': forms.Select(attrs={'class': 'form-select'}),
        }

class MadreForm(forms.ModelForm):
    # Accept both formatted and unformatted RUT input (dots/dash optional);
    # final formatting is applied in clean_rut().
    rut_validator = RegexValidator(
        regex=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$',
        message='El formato del RUT debe ser XX.XXX.XXX-X (por ejemplo: 12.345.678-9)'
    )
    rut = forms.CharField(
        validators=[rut_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '12345678-9',
            'pattern': r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$'
        })
    )

    def clean_rut(self):
        from .utils import normalize_rut, format_rut, validate_rut
        raw = self.cleaned_data.get('rut', '')

        # Si ya está en formato correcto, solo validamos
        if re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', raw):
            clean = re.sub(r'[^0-9kK]', '', raw).upper()
            if not validate_rut(clean):
                raise forms.ValidationError('El dígito verificador no coincide. Revise el último dígito del RUT')
            return raw

        # Si no está formateado, intentamos formatearlo
        clean = re.sub(r'[^0-9kK]', '', raw).upper()
        
        # Validaciones básicas
        if not clean or len(clean) < 2:
            raise forms.ValidationError('El formato del RUT debe ser XX.XXX.XXX-X (por ejemplo: 12.345.678-9)')
        
        number = clean[:-1]
        if not number.isdigit():
            raise forms.ValidationError('El RUT debe contener solo números y un dígito verificador')
        
        if int(number) < 1000000:
            raise forms.ValidationError('El RUT debe ser mayor a 1.000.000')
        
        # Si el RUT es válido, lo formateamos y retornamos
        if validate_rut(clean):
            formatted = format_rut(clean)
            # Si el formato resultante no coincide con el patrón esperado
            if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', formatted):
                raise forms.ValidationError('El formato del RUT debe ser XX.XXX.XXX-X (por ejemplo: 12.345.678-9)')
            return formatted
            
        raise forms.ValidationError('El dígito verificador no coincide. Revise el último dígito del RUT')
    
    class Meta:
        model = Madre
        fields = ['rut', 'nombres', 'apellidos', 'fecha_nacimiento', 
                 'estado_civil', 'direccion', 'telefono', 'prevision']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 XXXX XXXX'
            }),
            'prevision': forms.Select(attrs={'class': 'form-select'}),
        }

class PartoForm(forms.ModelForm):
    # The browser's datetime-local uses the 'T' separator (YYYY-MM-DDTHH:MM).
    # Provide a DateTimeField with matching input_formats and widget format so
    # the form will validate when the user submits from the template.
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }, format='%Y-%m-%dT%H:%M'),
        # Accept several common formats: browser 'datetime-local', ISO with space,
        # and the DD-MM-YYYY HH:MM format used by templates in this project.
        input_formats=[
            '%Y-%m-%dT%H:%M',  # browser datetime-local
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d-%m-%Y %H:%M',   # form uses day-month-year in templates
        ]
    )
    
    # Campos para "Trabajo de Parto"
    paridad = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '1'
        }),
        label="Paridad"
    )
    
    semanas_obstetricas = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '1'
        }),
        label="Semanas Obstétricas"
    )
    
    semanas_obstetricas_dias = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '1'
        }),
        label="Semanas Obstétricas (días)"
    )
    
    monitor = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Monitor"
    )
    
    ttc = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="TTC"
    )
    
    induccion = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Inducción"
    )
    
    tipo_parto = forms.ChoiceField(
        required=False,
        choices=[
            ('', '---------'),
            ('cesarea_urgencia', 'Cesárea Urgencia'),
            ('cesarea_electiva', 'Cesárea Electiva'),
            ('distocico', 'Distocico'),
            ('eutocico', 'Eutocico'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Parto"
    )
    
    alumbramiento_dirigido = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Alumbramiento dirigido"
    )
    
    clasificacion_robson = forms.ChoiceField(
        required=False,
        choices=[
            ('', '---------'),
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
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Clasificación de Robson"
    )
    
    acompanamiento_parto = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Acompañamiento Parto"
    )
    
    motivo_parto_no_acompanado = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese el motivo si el parto no fue acompañado'
        }),
        label="Motivo Parto NO acompañado"
    )
    
    persona_acompanante = forms.ChoiceField(
        required=False,
        choices=[
            ('', '---------'),
            ('pareja', 'Pareja'),
            ('hermano', 'Hermana/o'),
            ('padre_madre', 'Padre/Madre'),
            ('tio', 'Tía/o'),
            ('suegro', 'Suegra/o'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Persona Acompañante"
    )
    
    acompanante_secciona_cordon = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Acompañante secciona cordón"
    )
    
    # Campos para "Información de los profesionales"
    profesional_a_cargo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el nombre del profesional'
        }),
        label="Profesional a cargo",
        max_length=200
    )
    
    causa_cesarea = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese la causa de la cesárea si aplica'
        }),
        label="Causa cesárea"
    )
    
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese observaciones adicionales'
        }),
        label="Observaciones"
    )
    
    # Campos para "Otros registros"
    uso_sala_saip = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Uso sala SAIP"
    )
    
    ley_21372_dominga = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Cuales recuerdos (de no entregar justificar motivo)'
        }),
        label="Ley N° 21.372 Dominga",
        help_text="Cuales recuerdos (de no entregar justificar motivo)"
    )
    
    retira_placenta = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Retira placenta"
    )
    
    estampado_placenta = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Sí'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Estampado de placenta"
    )
    
    folio_valido = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el folio válido'
        }),
        label="Folio válido",
        max_length=100
    )
    
    folios_nulos = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese folio/s nulo/s'
        }),
        label="Folio/s Nulo/s",
        max_length=200
    )
    
    manejo_dolor_no_farmacologico = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese información sobre manejo del dolor no farmacológico'
        }),
        label="Manejo del dolor no farmacológico"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar queryset para profesional_a_cargo
        from cuentas.models import Usuario
        self.fields['profesional_a_cargo'].queryset = Usuario.objects.filter(is_active=True)
        
        # Prellenar profesional_a_cargo_display si hay un profesional seleccionado
        if self.instance and self.instance.pk and self.instance.profesional_a_cargo:
            prof = self.instance.profesional_a_cargo
            area = prof.rol.nombre if prof.rol else 'Sin área'
            self.initial['profesional_a_cargo_display'] = f"{prof.first_name or ''} {prof.last_name or ''} - {prof.run or ''} ({area})".strip()
        
        # Convertir valores booleanos existentes a strings para los ChoiceFields
        if self.instance and self.instance.pk:
            if self.instance.monitor is not None:
                self.initial['monitor'] = 'True' if self.instance.monitor else 'False'
            if self.instance.ttc is not None:
                self.initial['ttc'] = 'True' if self.instance.ttc else 'False'
            if self.instance.induccion is not None:
                self.initial['induccion'] = 'True' if self.instance.induccion else 'False'
            if self.instance.alumbramiento_dirigido is not None:
                self.initial['alumbramiento_dirigido'] = 'True' if self.instance.alumbramiento_dirigido else 'False'
            if self.instance.acompanamiento_parto is not None:
                self.initial['acompanamiento_parto'] = 'True' if self.instance.acompanamiento_parto else 'False'
            if self.instance.acompanante_secciona_cordon is not None:
                self.initial['acompanante_secciona_cordon'] = 'True' if self.instance.acompanante_secciona_cordon else 'False'
            if self.instance.uso_sala_saip is not None:
                self.initial['uso_sala_saip'] = 'True' if self.instance.uso_sala_saip else 'False'
            if self.instance.retira_placenta is not None:
                self.initial['retira_placenta'] = 'True' if self.instance.retira_placenta else 'False'
            if self.instance.estampado_placenta is not None:
                self.initial['estampado_placenta'] = 'True' if self.instance.estampado_placenta else 'False'
    
    def clean_monitor(self):
        value = self.cleaned_data.get('monitor')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_ttc(self):
        value = self.cleaned_data.get('ttc')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_induccion(self):
        value = self.cleaned_data.get('induccion')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_alumbramiento_dirigido(self):
        value = self.cleaned_data.get('alumbramiento_dirigido')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_acompanamiento_parto(self):
        value = self.cleaned_data.get('acompanamiento_parto')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_acompanante_secciona_cordon(self):
        value = self.cleaned_data.get('acompanante_secciona_cordon')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_uso_sala_saip(self):
        value = self.cleaned_data.get('uso_sala_saip')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_retira_placenta(self):
        value = self.cleaned_data.get('retira_placenta')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    def clean_estampado_placenta(self):
        value = self.cleaned_data.get('estampado_placenta')
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None
    
    class Meta:
        model = Parto
        fields = [
            'fecha_hora',
            'paridad',
            'semanas_obstetricas',
            'semanas_obstetricas_dias',
            'monitor',
            'ttc',
            'induccion',
            'tipo_parto',
            'alumbramiento_dirigido',
            'clasificacion_robson',
            'acompanamiento_parto',
            'motivo_parto_no_acompanado',
            'persona_acompanante',
            'acompanante_secciona_cordon',
            'profesional_a_cargo',
            'causa_cesarea',
            'observaciones',
            'uso_sala_saip',
            'ley_21372_dominga',
            'retira_placenta',
            'estampado_placenta',
            'folio_valido',
            'folios_nulos',
            'manejo_dolor_no_farmacologico',
        ]

class RecienNacidoForm(forms.ModelForm):
    class Meta:
        model = RecienNacido
        fields = ['hora_nacimiento', 'sexo', 'peso', 'talla', 
                 'apgar_1', 'apgar_5', 'estado', 'observaciones']
        widgets = {
            'hora_nacimiento': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.1',
                'max': '6.0'
            }),
            'talla': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '20',
                'max': '60'
            }),
            'apgar_1': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10'
            }),
            'apgar_5': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class PartoCompletoForm(forms.Form):
    """
    Formulario que combina los tres formularios anteriores para un registro completo
    """
    def __init__(self, *args, prefixes=None, allow_old_parto=False, **kwargs):
        """Initialize nested forms. If `prefixes` is provided it must be a
        3-tuple (madre_prefix, parto_prefix, recien_prefix) and will be used
        so each subform's HTML name/id are namespaced and avoid collisions
        when rendered together in a single <form>.
        """
        super().__init__(*args, **kwargs)
        if prefixes:
            madre_prefix, parto_prefix, recien_prefix = prefixes
            self.madre_form = MadreForm(*args, prefix=madre_prefix, **kwargs)
            self.parto_form = PartoForm(*args, prefix=parto_prefix, **kwargs)
            self.recien_nacido_form = RecienNacidoForm(*args, prefix=recien_prefix, **kwargs)
        else:
            self.madre_form = MadreForm(*args, **kwargs)
            self.parto_form = PartoForm(*args, **kwargs)
            self.recien_nacido_form = RecienNacidoForm(*args, **kwargs)
        # If caller requests allowing old parto registration, set a flag on the
        # provisional Parto instance so its model-level clean() can bypass the
        # 48-hour restriction.
        try:
            if allow_old_parto:
                setattr(self.parto_form.instance, '_allow_old_parto', True)
        except Exception:
            pass
        
    def is_valid(self):
        madre_ok = self.madre_form.is_valid()
        parto_ok = self.parto_form.is_valid()
        if not (madre_ok and parto_ok):
            # still run recien_nacido_form.is_valid to populate errors, but without provisional context
            self.recien_nacido_form.is_valid()
            return False

        # Attach provisional parto datetime to the recien_nacido instance so its clean() can use it
        provisional_dt = self.parto_form.cleaned_data.get('fecha_hora')
        if provisional_dt:
            try:
                # set attributes on the model instance used by the form so RN.clean can use them
                self.recien_nacido_form.instance._parto_fecha_hora = provisional_dt
                semanas = self.parto_form.cleaned_data.get('semanas_gestacion')
                if semanas is not None:
                    # attach provisional semanas as integer
                    try:
                        self.recien_nacido_form.instance._parto_semanas = int(semanas)
                    except Exception:
                        pass
            except Exception:
                pass

        rn_ok = self.recien_nacido_form.is_valid()
        # If RN form reported invalid but has no errors (some model-level
        # ValidationError can be missed in edge cases), try to run the
        # model-level clean and attach messages explicitly so callers/tests
        # can inspect `recien_nacido_form.errors` reliably.
        if not rn_ok and not self.recien_nacido_form.errors:
            from django.core.exceptions import ValidationError
            try:
                # Ensure provisional context is present on instance
                inst = self.recien_nacido_form.instance
                # Call model.clean() directly to surface ValidationError
                inst.clean()
            except ValidationError as e:
                # Attach all messages as non-field errors on the RN form
                for msg in getattr(e, 'messages', [str(e)]):
                    self.recien_nacido_form.add_error(None, msg)
                rn_ok = False
            except Exception:
                # If something else fails, mark RN as invalid to be safe
                self.recien_nacido_form.add_error(None, 'Error en validación de recién nacido')
                rn_ok = False

        return madre_ok and parto_ok and rn_ok

    def save(self, commit=True):
        if not self.is_valid():
            raise ValueError("Formulario no válido")
            
        madre = self.madre_form.save(commit=commit)
        if commit:
            parto = self.parto_form.save(commit=False)
            parto.madre = madre
            parto.save()
            
            recien_nacido = self.recien_nacido_form.save(commit=False)
            recien_nacido.parto = parto
            recien_nacido.save()
            
            return madre, parto, recien_nacido
        return madre