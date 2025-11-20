# Prototipo PI1 - Obstetricia

Resumen rápido

Este repositorio contiene una aplicación Django para registro de partos (madres, partos, recién nacidos). Incluye utilidades de búsqueda/creación rápida de madre, exportes a Excel y formularios compuestos.

Requisitos

- Python 3.10+ (este repo se ha probado en 3.11/3.12 en desarrollo)
- Virtualenv / venv
- Dependencias listadas en `requirements.txt` (si no existe, instale Django y pandas/openpyxl):

    pip install django pandas openpyxl

Configuración local (Windows PowerShell)

```powershell
# Crear virtualenv
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"

# Instalar dependencias
pip install -r requirements.txt  # si existe
# o mínimo
pip install django pandas openpyxl

# Migraciones
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

Pruebas

```powershell
& ".\.venv\Scripts\Activate.ps1"
python manage.py test
```

Notas de seguridad (producción)

- Asegúrese de configurar `DEBUG = False` en `obstetricia/settings.py`.
- Establezca `ALLOWED_HOSTS` apropiadamente.
- Habilite `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, y HSTS (`SECURE_HSTS_SECONDS`).
- Use un secreto fuerte en `SECRET_KEY` (no lo deje en el repo).


Mejoras aplicadas en esta ronda

- Tests básicos para el endpoint `madre_create` (happy path + duplicate RUT).
- Validación cliente en modal "Crear Madre" para evitar envíos vacíos.
- Índices DB sugeridos en campos frecuentemente consultados (`Madre.rut`, `Parto.fecha_hora`, `RecienNacido.hora_nacimiento`).

Viñetas categorizadas

Las siguientes viñetas están organizadas por categorías para facilitar la documentación y la visualización en el sitio estático incluido en `site/`.

- **Descripción**: Breve resumen del proyecto y su propósito.
    - Prototipo para el registro y gestión de partos.
    - Permite registrar madres, partos y recién nacidos.
    - Incluye herramientas para búsqueda y exportes.

- **Características**: Funcionalidades destacadas.
    - Formularios compuestos con validación cliente y servidor.
    - Exportes a Excel (pandas / openpyxl).
    - Búsqueda rápida de madres por RUT y filtros por fecha.
    - Panel administrativo con permisos básicos.

- **Uso**: Pasos rápidos para comenzar.
    - Crear y activar un entorno virtual.
    - Instalar dependencias y ejecutar `migrate`.
    - Crear superusuario y levantar `runserver`.

- **Mantenimiento**: Recomendaciones para producción y mantenimiento.
    - Configurar `DEBUG = False` y `ALLOWED_HOSTS`.
    - Usar variables de entorno para `SECRET_KEY` y credenciales.
    - Agregar monitoreo y backups para la base de datos.

- **Contacto / Soporte**: Cómo obtener ayuda.
    - Abrir un issue en el repositorio con información reproducible.
    - Incluir logs y pasos para reproducir el problema.

Siguientes pasos recomendados

- Ejecutar `python manage.py makemigrations` y revisar migraciones.
- Añadir más tests de integración para el flujo completo de registro de parto.
- Añadir CI (GitHub Actions) para ejecutar tests automáticamente.
- Revisión de accesibilidad y consistencia visual de la UI.

Instrucciones para el sitio estático

El directorio `site/` contiene una versión estática simple (HTML + CSS) que muestra las viñetas categorizadas. Puedes abrir `site/index.html` en tu navegador para ver la página localmente.

Si quieres que integre este contenido dentro de las plantillas Django en vez de un sitio estático, dime y lo integro en `templates/`.

Página integrada en Django

También agregué una plantilla integrada en Django en `templates/site_info.html`, una vista en `obstetricia/site_views.py` y una URL en `obstetricia/urls.py` disponible en `/info/` cuando el servidor de desarrollo está en marcha.

Ejemplo (ejecutar desde la raíz del proyecto):

```powershell
& ".\.venv\Scripts\Activate.ps1"
python manage.py runserver
# Abrir en navegador: http://127.0.0.1:8000/info/
```

Publicar la página estática en GitHub Pages (opción rápida)

Si quieres que la gente vea la página estática (`site/index.html`) sin ejecutar Django, publica `site/` en GitHub Pages. Incluí un workflow de GitHub Actions y un script local para facilitarlo.

- Archivo de Actions: `.github/workflows/gh-pages.yml` — despliega `site/` a la rama `gh-pages` en cada push a `main`.
- Script local: `deploy_site.ps1` — empuja `site/` a `gh-pages` usando `git subtree push --prefix site origin gh-pages`.

Pasos rápidos:

1. Crea un repositorio en GitHub y conecta tu remoto `origin`:

```powershell
git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
git push -u origin main
```

2a (Automático): Usar GitHub Actions — tras pushear a `main` el workflow `.github/workflows/gh-pages.yml` publicará `site/` en la rama `gh-pages` y GitHub Pages servirá esa rama.

2b (Manual/local): correr el script PowerShell desde la raíz del proyecto (requiere `git` y remote `origin` configurado):

```powershell
.\deploy_site.ps1
```

3. Activar GitHub Pages en el repo: en GitHub, ve a Settings → Pages y selecciona la rama `gh-pages` como fuente (si no se habilita automáticamente). El sitio estará en `https://<tu-usuario>.github.io/<tu-repo>/`.

Nota: Si prefieres que el sitio esté en la ruta `/<repo>/`, usa la rama `gh-pages`. Otra opción es poner los archivos en la carpeta `/docs` de `main` y usar esa carpeta como fuente en Pages.

Despliegue de la aplicación Django completa (opción b)

Si quieres que el backend Django esté disponible públicamente (login, exportes, base de datos), una opción sencilla es usar Render (o PythonAnywhere). Para preparar el repo incluí `requirements.txt` y `Procfile` y realicé cambios para leer secretos desde variables de entorno.

Pasos rápidos para Render (ejemplo):

1. Asegúrate de que `requirements.txt` y `Procfile` estén en la raíz del repo (ya están añadidos).
2. Empuja tu repo a GitHub y crea un nuevo Web Service en Render conectado a tu repo.
    - Build command: `pip install -r requirements.txt`
    - Start command: `gunicorn obstetricia.wsgi`
3. En la sección "Environment" de Render, añade variables de entorno necesarias:
    - `DJANGO_SECRET_KEY` (string fuerte)
    - `DJANGO_DEBUG` = `False`
    - `DJANGO_ALLOWED_HOSTS` = `yourdomain.com` (o la URL proporcionada por Render)
    - Configura la base de datos: Render ofrece Postgres; si usas MySQL, añade `DATABASE_URL` o configura las credenciales según tu proveedor.
4. Ejecuta migraciones en el servicio Render (puedes usar la consola de Render o un deploy hook):
    - `python manage.py migrate`
    - `python manage.py collectstatic --noinput`

Ejemplo comandos locales antes de deploy (PowerShell):

```powershell
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt
python manage.py collectstatic --noinput
git add .
git commit -m "Preparar despliegue Django: requirements + Procfile + settings prod"
git push origin main
```

PythonAnywhere (alternativa simple): sube el repo o usa GitHub import, configura un "Web App" con WSGI, crea un virtualenv con las mismas dependencias y configura variables de entorno en la sección Web → Environment variables.

Importante — configuración segura de `settings.py`:

- `DJANGO_SECRET_KEY`: obligatorio en producción. No dejes el secreto por defecto en el repo.
- `DJANGO_DEBUG=False` en producción.
- `DJANGO_ALLOWED_HOSTS`: lista de dominios permitidos.
- `STATIC_ROOT` ya está configurado en `settings.py`; recuerda ejecutar `collectstatic`.

Si quieres que yo haga los pasos finales para Render (crear el servicio y añadir los env vars no es posible desde aquí), puedo generar un `render.yaml` o un ejemplo de comandos para la consola de Render y una guía paso a paso con las variables exactas a rellenar.

Si quieres que aplique migraciones, añada más tests o configure CI, dime cuál prefieres y lo hago.
