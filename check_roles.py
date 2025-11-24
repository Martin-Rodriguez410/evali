import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obstetricia.settings")
django.setup()

from cuentas.models import Rol, Usuario
from usuarios.models import Perfil

print("Roles in cuentas.Rol:")
for r in Rol.objects.all():
    print(f"- {r.nombre}")

print("\nUsers and their roles:")
for u in Usuario.objects.all():
    rol_name = u.rol.nombre if u.rol else "No Role"
    print(f"- {u.username}: {rol_name}")
    try:
        perfil = Perfil.objects.get(user=u)
        print(f"  Perfil role: {perfil.rol}")
    except Perfil.DoesNotExist:
        print("  No Perfil")
