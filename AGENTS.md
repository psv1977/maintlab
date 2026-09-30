# Propósito y alcance
- El MVP existente incluye gestión de equipos, mantenimientos e historial, organizaciones y aislamiento multi-tenant, gestión de usuarios, entregas, dashboard y búsqueda universal.
- Las apps existentes son `equipment`, `maintenance`, `organizations`, `users`, `deliveries` y `dashboard`. Mantener sus dependencias desacopladas y respetar el aislamiento por organización en modelos, vistas, formularios, consultas y pruebas.
- CSV de equipos es una extensión posterior de `001-equipment`, no una app ni una feature independiente. La búsqueda universal se documenta en `006-dashboard-search`; no duplicar esa especificación en `001-equipment`.
- Materiales e inventario son post-MVP: mantener el diseño extensible, pero no implementar esas funciones ni crear sus apps aún.
- El estado funcional y su trazabilidad SDD se documentan en `spec/features/001-equipment/` y `spec/features/002-maintenance/` a `spec/features/006-dashboard-search/`. Las especificaciones 002–006 son retroactivas y describen funcionalidad existente.

# Contexto persistente del proyecto
- Consultar `MEMORY.md` al iniciar una nueva sesión o retomar trabajo después de una interrupción, antes de realizar una exploración amplia del repositorio.
- `MEMORY.md` es contexto de apoyo; no reemplaza las especificaciones SDD, el código ni los tests vigentes.
- Documentar las nuevas decisiones funcionales en la especificación correspondiente.

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
