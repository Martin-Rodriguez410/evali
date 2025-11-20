from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.utils import timezone
from .models import Parto

def exportar_datos_pdf(fecha_inicio=None, fecha_fin=None):
    """
    Genera un reporte PDF de los partos.
    """
    partos_qs = Parto.objects.select_related('madre', 'created_by').prefetch_related('recien_nacidos').order_by('-fecha_hora')

    if fecha_inicio and fecha_fin:
        partos = partos_qs.filter(fecha_hora__date__range=[fecha_inicio, fecha_fin])
        rango_fechas = f"Desde {fecha_inicio} hasta {fecha_fin}"
    else:
        partos = partos_qs[:500] # Limit to 500 for PDF to avoid timeout/memory issues if too large
        rango_fechas = "Todos los registros (Últimos 500)"

    template_path = 'registros/pdf_report.html'
    context = {
        'partos': partos,
        'fecha_generacion': timezone.now(),
        'rango_fechas': rango_fechas,
        'usuario_generador': 'Sistema' # Can be updated if request user is passed
    }

    response = HttpResponse(content_type='application/pdf')
    filename = f"Reporte_Partos_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
       html, dest=response
    )

    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
