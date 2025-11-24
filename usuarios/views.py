from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Perfil

    
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']  
        password = request.POST['password']
        usuario = authenticate(request, username=username, password=password)
    if usuario is not None:
        login(request, usuario)
        return redirect('blog:lista_articulos')
    else:
        messages.error(request, 'Nombre de usuario o contraseña erroneos')
    return render(request, 'usuarios/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('usuarios:login')

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model

User = get_user_model()

def es_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(es_superuser)
def lista_profesionales(request):
    profesionales = User.objects.filter(is_active=True).exclude(is_superuser=True)
    return render(request, 'usuarios/lista_profesionales.html', {'profesionales': profesionales})

@login_required
@user_passes_test(es_superuser)
def despedir_profesional(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=user_id)
            if not user.is_superuser:
                user.is_active = False
                user.save()
                messages.success(request, f'El profesional {user.username} ha sido despedido (desactivado).')
            else:
                messages.error(request, 'No puedes despedir a un superusuario.')
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
    return redirect('usuarios:lista_profesionales')






