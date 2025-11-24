import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obstetricia.settings")
django.setup()

from cuentas.models import Rol, Usuario
from usuarios.models import Perfil

# 1. Ensure 'Administrador' role exists
admin_rol, created = Rol.objects.get_or_create(nombre='Administrador')
if created:
    print("Created 'Administrador' role.")
else:
    print("'Administrador' role already exists.")

# 2. Update 'Admin' user
try:
    admin_user = Usuario.objects.get(username='Admin')
    
    # Update Usuario.rol
    admin_user.rol = admin_rol
    admin_user.save()
    print(f"Updated Usuario 'Admin' role to '{admin_rol.nombre}'.")

    # Update Perfil.rol (if it exists)
    try:
        perfil = Perfil.objects.get(user=admin_user)
        perfil.rol = 'administrador' # Matches the choice in Perfil model
        perfil.save()
        print(f"Updated Perfil for 'Admin' to 'administrador'.")
    except Perfil.DoesNotExist:
        # Create profile if it doesn't exist
        Perfil.objects.create(user=admin_user, rol='administrador')
        print(f"Created Perfil for 'Admin' with role 'administrador'.")

except Usuario.DoesNotExist:
    print("User 'Admin' not found.")
