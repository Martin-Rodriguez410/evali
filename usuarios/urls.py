from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profesionales/', views.lista_profesionales, name='lista_profesionales'),
    path('profesionales/despedir/<int:user_id>/', views.despedir_profesional, name='despedir_profesional'),
]
