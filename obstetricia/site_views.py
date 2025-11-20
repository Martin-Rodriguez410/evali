from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def site_info(request):
    """Página simple que muestra la información del proyecto (viñetas).

    Esta vista ahora requiere autenticación; usuarios anónimos serán
    redirigidos a `settings.LOGIN_URL`.
    """
    return render(request, "site_info.html")
