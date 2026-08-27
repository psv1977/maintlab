# Propósito y alcance
- MVP: registrar equipos, registrar mantenimientos, consultar el historial y gestionar usuarios.
- Materiales e inventario son post-MVP: mantener el diseño extensible, pero no implementar esas funciones ni crear sus apps aún.

# Stack y restricciones
- Backend: Python/Django con SQLite inicialmente y configuración en `maintlab/settings.py`. No cambiar de base de datos ni instalar dependencias sin autorización.
- Versión objetivo de Python: 3.13.x, por compatibilidad con el entorno de despliegue (actualmente Python 3.13.15). No modificar ni sustituir el Python del sistema operativo.
- `.venv/`, `.env`, `db.sqlite3` y `db.sqlite3-journal` son estado local ignorado; no modificarlos ni confirmarlos.
- No alterar la arquitectura sin autorización.

# Estructura prevista
- Proyecto: `manage.py` en raíz y paquete `maintlab/`, con `settings.py`, `urls.py`, `wsgi.py` y `asgi.py`.
- Apps MVP: `equipment`, `maintenance` y `users`. Mantener sus dependencias desacopladas para permitir futuras apps de inventario o materiales.
- Frontend: Django templates y forms; mantener `forms.py`, `views.py`, `urls.py` y `admin.py` dentro de cada app.

# Convenciones y permisos
- Código, identificadores, modelos y migraciones en inglés. Documentación, docstrings y commits en español.
- Usar el modelo `User` estándar de `django.contrib.auth`; no implementar un RBAC personalizado en el MVP.
- Usar el grupo `tecnicos`: puede crear, consultar y editar equipos y registros de mantenimiento, pero no eliminarlos.
- La administración usa `is_staff` e `is_superuser`; no crear un grupo `admin`.
- Definir permisos mediante los mecanismos estándar de Django y mantener el diseño abierto a nuevos grupos o permisos.

# Pruebas y límites
- Incluir pruebas para cada funcionalidad. Cuando `pytest-django` esté configurado, usar `pytest` como ejecutor.
- No implementar inventario, materiales, DRF, SPA ni una migración fuera de SQLite durante el MVP.
