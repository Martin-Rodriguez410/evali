# Despliegue en Render

Este repositorio incluye un `render.yaml` para crear automáticamente un Web Service y una base de datos PostgreSQL en Render.

Pasos rápidos:

1. Crea una cuenta en Render: https://dashboard.render.com
2. Conecta tu cuenta con GitHub y autoriza el repositorio `martinrodrigueztoro03-sketch/proyecto`.
3. Desde el Dashboard selecciona **New → Web Service** o simplemente crea un servicio apuntando al repo/branch `main`. Render detectará el archivo `render.yaml` y propondrá crear el servicio `proyecto-web` y la base de datos `proyecto-db`.
4. En el panel del servicio, ve a **Environment** y añade las variables de entorno necesarias:
   - `DJANGO_SECRET_KEY` — valor secreto (génial: `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
   - `DJANGO_DEBUG` — `False`
   - `DJANGO_ALLOWED_HOSTS` — la URL que Render asigne, por ejemplo `proyecto-web.onrender.com` (puedes usar `*` temporalmente durante pruebas)
   - `DATABASE_URL` — si creas la base de datos desde Render, el valor se crea automáticamente; si no, pégalo manualmente.

5. Ejecuta migraciones y collectstatic usando la consola de Render (en el Service → Shell):
```
python manage.py migrate
python manage.py collectstatic --noinput
```

6. Revisa los logs en caso de errores y abre la URL pública desde el Dashboard.

Notas:
- `Procfile` ya existe y `render.yaml` usa `gunicorn` para arrancar la app.
- `obstetricia/settings.py` ya soporta `DATABASE_URL` y WhiteNoise para servir estáticos.
- Si necesitas almacenar archivos media en producción, configura un storage externo (S3) y añade sus credenciales como variables de entorno.

Si quieres, puedo:
- Generar aquí el `DJANGO_SECRET_KEY` y sugerirte valores para `DJANGO_ALLOWED_HOSTS`.
- Ayudarte a resolver errores de build si aparecen tras conectar el repo.
