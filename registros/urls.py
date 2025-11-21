from django.urls import path
from . import views
from . import views_reportes

app_name = 'registros'

urlpatterns = [
    path('registro/', views.registro_parto, name='registro_parto'),
    path('registro/madre/<int:madre_id>/', views.registro_parto, name='registro_parto_madre'),
    path('lista/', views.lista_partos, name='lista_partos'),
    path('madres/', views.lista_madres, name='lista_madres'),
    path('exportar/excel/', views.exportar_partos, name='exportar_partos'),
    path('exportar/pdf/', views.exportar_partos_pdf, name='exportar_partos_pdf'),
    path('importar/', views.importar_partos, name='importar_partos'),
    path('api/madre/', views.madre_lookup, name='madre_lookup'),
    path('api/madre_create/', views.madre_create, name='madre_create'),
    path('madre/create/page/', views.madre_create_page, name='madre_create_page'),
    path('api/madre_typeahead/', views.madre_typeahead, name='madre_typeahead'),
    path('api/profesionales/', views.profesionales_list, name='profesionales_list'),
    path('detalle/<int:parto_id>/', views.detalle_parto, name='detalle_parto'),
    path('editar/<int:parto_id>/', views.editar_parto, name='editar_parto'),
    path('reportes/', views_reportes.reporte_rem, name='reporte_rem'),
]