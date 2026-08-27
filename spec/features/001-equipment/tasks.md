# Tareas: Gestión de equipos (001-equipment)

Derivado estrictamente de `spec.md` y `plan.md`. Convenciones globales:
código e identificadores en inglés; documentación, comentarios de commit,
docstrings y textos visibles en español. Ejecución secuencial T01→T19;
ninguna tarea comienza si la anterior no cierra en verde con su commit.

> **Nota de trazabilidad:** spec §6 reserva el retiro a `is_staff`/`is_superuser`,
> pero la decisión D6 del plan lo resolvió como autorización exclusiva por el
> permiso `retire_equipment` (el superusuario pasa implícitamente; el grupo
> `tecnicos` nunca recibe dicho permiso). Estas tareas implementan D6.

Verificación base de cada tarea (desde la raíz del proyecto):
`source .venv/bin/activate && pytest` y, donde aplique,
`python manage.py check` / `python manage.py makemigrations --check`.

---

## Fase 1 — Infraestructura

### T01 — Entorno Python y dependencias
- **Objetivo:** instalar y gestionar de forma aislada Python 3.13.15 para
  recrear `.venv` con ese intérprete, junto con Django 5.2 LTS, `pytest` y
  `pytest-django` (D1/D2), sin modificar ni sustituir el Python del sistema
  operativo.
- **Archivos afectados:** `.venv/` (estado local ignorado), `requirements.txt`.
- **Depende de:** ninguna. Se ejecuta únicamente con la orden expresa
  Plan → Build.
- **Criterio de finalización:** `python --version` reporta 3.13.15 y `.venv`
  fue recreado con ese intérprete;
  `django-admin --version` reporta 5.2.x; `pip check` sin conflictos;
  `requirements.txt` versionado con versiones fijadas; nada de `.venv/`
  en git.
- **Pruebas / verificación:** comandos anteriores; aún no hay suite.

### T02 — Proyecto base Django
- **Objetivo:** crear el proyecto `maintlab` con `manage.py` en raíz y la
  configuración base (D9, D11).
- **Archivos afectados:** `manage.py`, `maintlab/__init__.py`,
  `maintlab/settings.py`, `maintlab/urls.py`, `maintlab/wsgi.py`,
  `maintlab/asgi.py`, `templates/base.html` (esqueleto mínimo, D11),
  `.gitignore` (verificar exclusiones locales).
- **Depende de:** T01.
- **Criterio de finalización:** en `settings.py`: `LANGUAGE_CODE = "es"`,
  `USE_TZ = True`, `TIME_ZONE = "America/Santiago"` (D9) y
  `TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]` (D11);
  `manage.py migrate` aplica las apps por defecto (crea `db.sqlite3`
  local, ignorado); `manage.py runserver` arranca correctamente, sin
  exigir una respuesta concreta (p. ej. HTTP 200) en `/`.
- **Pruebas / verificación:** `manage.py check` sin errores; suite aún
  no existe.

### T03 — Configurar pytest-django
- **Objetivo:** dejar operativo el ejecutor de pruebas con BD SQLite en
  memoria (estrategia del plan §5).
- **Archivos afectados:** `pytest.ini`; prueba de humo temporal
  `maintlab/test_smoke.py` (se elimina en T05).
- **Depende de:** T02.
- **Criterio de finalización:** `pytest.ini` define
  `DJANGO_SETTINGS_MODULE = maintlab.settings`; `pytest` ejecuta el humo
  en verde contra BD de pruebas en memoria; el humo está marcado como
  temporal.
- **Pruebas / verificación:** `pytest` verde (humo).

---

## Fase 2 — Dominio, permisos e integridad

### T04 — App `equipment`
- **Objetivo:** crear la app MVP y registrarla en el proyecto.
- **Archivos afectados:** `equipment/` (generado por `startapp`),
  conversión de `equipment/tests.py` en paquete
  `equipment/tests/__init__.py`, `maintlab/settings.py`
  (`INSTALLED_APPS`).
- **Depende de:** T03.
- **Criterio de finalización:** `manage.py check` sin errores; la app
  aparece instalada; sin URLs ni modelos todavía.
- **Pruebas / verificación:** `manage.py check`; `pytest` sigue en verde.

### T05 — Modelo `Equipment` (+tests)
- **Objetivo:** implementar el modelo según plan §3.3 (campos, longitudes
  D10, `on_delete=PROTECT` D3, `updated_*` nulos hasta primera edición,
  sin `auto_now` en `updated_at`), con `__str__`, `Meta.ordering` y
  `TextChoices` con etiquetas en español (spec §5). Sin
  `Meta.permissions` todavía (va en T07).
- **Archivos afectados:** `equipment/models.py`;
  `equipment/tests/test_models.py`; eliminar `maintlab/test_smoke.py`.
- **Depende de:** T04.
- **Criterio de finalización:** modelo completo y validado con
  `full_clean()` en tests; valores por defecto correctos.
- **Pruebas / verificación** (`test_models.py`): creación válida;
  `status` inicial `operational`; `updated_by` y `updated_at` nulos al
  crear; `created_at` automático; rechazo de exceder `max_length`;
  rechazo de `status` fuera del catálogo; `__str__` legible; `ordering`
  aplicado. Suite completa en verde.

### T06 — Migraciones iniciales
- **Objetivo:** materializar el modelo en la BD SQLite.
- **Archivos afectados:** `equipment/migrations/0001_initial.py`.
- **Depende de:** T05.
- **Criterio de finalización:** `manage.py makemigrations --check
  --dry-run` limpio; `manage.py migrate` aplica sin errores.
- **Pruebas / verificación:** comandos anteriores; suite en verde.

### T07 — Permiso `retire_equipment` (+tests)
- **Objetivo:** declarar el permiso personalizado en
  `Meta.permissions` (plan §3.4) y generar su migración.
- **Archivos afectados:** `equipment/models.py` (Meta),
  `equipment/migrations/0002_*.py`, `equipment/tests/test_permissions.py`.
- **Depende de:** T06.
- **Criterio de finalización:** permiso registrado en el content type de
  `Equipment`; otorgable mediante los mecanismos estándar de Django.
- **Pruebas / verificación** (`test_permissions.py`): el permiso existe;
  un usuario con el permiso asignado directamente pasa `has_perm`;
  un usuario común no lo tiene; el superusuario lo tiene implícitamente.
  Suite en verde.

### T08 — Bloqueo de eliminación física fuera de la UI (+tests)
- **Objetivo:** guard `pre_delete` que impida todo borrado de
  `Equipment`, por instancia y por queryset, incluido el borrado masivo
  del Admin (D4; plan §3.5). Ubicación sugerida: `equipment/signals.py`
  registrado en `AppConfig.ready()`.
- **Archivos afectados:** `equipment/signals.py`, `equipment/apps.py`,
  `equipment/tests/test_deletion.py`.
- **Depende de:** T07.
- **Criterio de finalización:** ningún camino programático elimina filas
  de `Equipment`; la excepción es controlada (p. ej.
  `ProtectedError` relanzada o equivalente).
- **Pruebas / verificación** (`test_deletion.py`):
  `instance.delete()` falla y el objeto persiste; `queryset.delete()`
  falla y los objetos persisten. Suite en verde.

### T09 — Grupo `tecnicos` por migración de datos (+tests)
- **Objetivo:** crear el grupo `tecnicos` con exactamente
  `add/view/change_equipment`, jamás `delete_equipment` ni
  `retire_equipment`, de forma idempotente (D5).
- **Archivos afectados:** `equipment/migrations/0003_*.py` (data
  migration), `equipment/tests/test_groups.py`.
- **Depende de:** T08.
- **Criterio de finalización:** migración aplicable dos veces sin efecto
  colateral (idempotente); el grupo queda con exactamente esos tres
  permisos.
- **Pruebas / verificación** (`test_groups.py`): el grupo existe tras
  migrar; su conjunto de permisos es exactamente el acordado; un
  miembro del grupo tiene add/view/change y no tiene delete ni retire;
  reejecutar la migración no duplica ni altera permisos. Suite en verde.

---

## Fase 3 — Formulario, URLs y vistas

### T10 — `EquipmentForm` (+tests)
- **Objetivo:** ModelForm con campos `name`, `code`, `description`,
  `serial_number`, `status`; choices de `status` sin `retired` (los
  técnicos nunca pueden enviarlo); unicidad de `code` vía validador del
  modelo (plan §3.6).
- **Archivos afectados:** `equipment/forms.py`,
  `equipment/tests/test_forms.py`.
- **Depende de:** T09.
- **Criterio de finalización:** el formulario valida y rechaza según
  spec §8.
- **Pruebas / verificación** (`test_forms.py`): datos válidos pasan;
  `name` y `code` requeridos; código duplicado rechazado;
  `description` y `serial_number` opcionales; `status=retired` ausente
  de choices y rechazado; `status` inválido rechazado. Suite en verde.

### T11 — Estructura de URLs
- **Objetivo:** definir el espacio de nombres `app_name = "equipment"`
  bajo `/equipment/` con las rutas nombradas `list`, `detail`, `create`,
  `update`, `retire` (plan §3.7).
- **Archivos afectados:** `equipment/urls.py`, `maintlab/urls.py`
  (include), vistas provisionales tipo stub en `equipment/views.py`
  (se reemplazan en T12–T16).
- **Depende de:** T10.
- **Criterio de finalización:** los cinco nombres resuelven con
  `reverse()`; `manage.py check` sin errores.
- **Pruebas / verificación:** `manage.py shell -c` con `reverse()` de
  los cinco nombres; `manage.py check`; suite en verde (sin archivo de
  tests nuevo: la cobertura llega con las vistas).

### T12 — Listado, detalle, login temporal y paginación (+tests)
- **Objetivo:** `ListView` con `paginate_by = 20` (D8) y `DetailView`,
  ambas con `LoginRequiredMixin`; habilitar `django.contrib.auth.urls`
  de forma temporal con su plantilla de login mínima (D7) y `LOGIN_URL`
  en settings.
- **Archivos afectados:** `equipment/views.py`, `equipment/urls.py`,
  `maintlab/urls.py`, `maintlab/settings.py`,
  `templates/base.html` (funcional mínimo),
  `templates/registration/login.html` (mínima),
  `equipment/templates/equipment/equipment_list.html` y
  `equipment_detail.html` (básicas),
  `equipment/tests/test_views_list.py`.
- **Depende de:** T11.
- **Criterio de finalización:** navegable de listado→detalle tras login;
  paginación operativa; anónimos redirigidos a login.
- **Pruebas / verificación** (`test_views_list.py`): anónimo →
  redirección a login; autenticado ve el listado; detalle muestra los
  campos; con 21 equipos hay 2 páginas y la página 2 funciona; los
  equipos `retired` aparecen en el listado. Suite en verde.

### T13 — Búsqueda y filtro por estado (+tests)
- **Objetivo:** parámetro GET `q` con `icontains` OR sobre `code`,
  `name`, `serial_number`; parámetro `status` exacto; combinables;
  estado inválido ignorado; retirados siempre consultables (plan §3.7,
  spec §7.2).
- **Archivos afectados:** `equipment/views.py` (get_queryset),
  `equipment_list.html` (formulario de búsqueda mínimo),
  `equipment/tests/test_views_search.py`.
- **Depende de:** T12.
- **Criterio de finalización:** búsqueda y filtro funcionan solos y
  combinados, sin romper la paginación.
- **Pruebas / verificación** (`test_views_search.py`): `q` encuentra por
  código, nombre y número de serie, insensible a mayúsculas, con OR;
  filtro exacto por estado; `q` + `status` combinados; `status`
  inválido se ignora (listado completo, sin error); un `retired` es
  hallazgo válido de búsqueda. Suite en verde.

### T14 — Alta con auditoría (+tests)
- **Objetivo:** `CreateView` con `form_valid` que asigna `created_by`;
  `created_at` automático; éxito redirige al listado (spec §7.1);
  estado inicial siempre `operational`.
- **Archivos afectados:** `equipment/views.py`, `equipment/urls.py`,
  `equipment_form.html` (básica), enlace «Nuevo equipo» en el listado,
  `equipment/tests/test_views_create.py`.
- **Depende de:** T13.
- **Criterio de finalización:** alta funcional con auditoría completa
  según spec §8.
- **Pruebas / verificación** (`test_views_create.py`): POST válido crea
  equipo en `operational`, con `created_by` = usuario actual,
  `created_at` presente y `updated_by`/`updated_at` vacíos; sin `name`
  o sin `code` se rechaza; código duplicado rechazado; anónimo
  redirigido; tras crear se aterriza en el listado. Suite en verde.

### T15 — Edición con auditoría y estados permitidos (+tests)
- **Objetivo:** `UpdateView` cuyo `form_valid` asigna `updated_by` y
  `updated_at` manualmente en cada guardado (nunca `auto_now`);
  refuerzo en servidor: un técnico no puede fijar `status=retired` ni
  siquiera manipulando el POST (choices del formulario + validación en
  la vista); unicidad de `code` preservada (spec §7.3, §8).
- **Archivos afectados:** `equipment/views.py`, `equipment/urls.py`,
  enlaces de edición en listado/detalle,
  `equipment/tests/test_views_update.py`.
- **Depende de:** T14.
- **Criterio de finalización:** edición funcional con auditoría
  incremental y blindaje anti-`retired`.
- **Pruebas / verificación** (`test_views_update.py`): edición válida
  persiste cambios; primera edición fija `updated_by` y `updated_at`;
  segunda edición refresca ambos; código de otro equipo rechazado y el
  propio aceptado; POST forjado con `status=retired` de un técnico no
  se aplica; transiciones entre `operational`, `in_maintenance` y
  `out_of_service` permitidas; anónimo redirigido. Suite en verde.

### T16 — Retiro autorizado (+tests)
- **Objetivo:** acción dedicada de retiro: GET muestra confirmación,
  POST ejecuta el cambio a `retired`; protección exclusiva por
  `PermissionRequiredMixin` con `retire_equipment` (D6); conserva todos
  los datos y deja el equipo consultable (spec §7.4).
- **Archivos afectados:** `equipment/views.py`, `equipment/urls.py`,
  `equipment_confirm_retire.html`, botón/acción «Retirar» condicionado
  a `{{ perms.equipment.retire_equipment }}` en listado/detalle,
  `equipment/tests/test_views_retire.py`.
- **Depende de:** T15.
- **Criterio de finalización:** retiro operativo solo para quien posea
  el permiso; sin ningún camino hacia borrado.
- **Pruebas / verificación** (`test_views_retire.py`): usuario con el
  permiso ve la confirmación (GET) y retira (POST); tras retirar, los
  datos permanecen y el equipo sigue en listado/detalle/búsqueda;
  miembro de `tecnicos` recibe denegación (403) en GET y POST; anónimo
  redirigido a login; GET no muta estado; superusuario retira
  implícitamente. Suite en verde.

---

## Fase 4 — Interfaz y administración

### T17 — Plantillas consistentes en español
- **Objetivo:** pulir `base.html` y las cuatro plantillas del app con
  navegación, mensajes, paginación visible y textos/etiquetas de estado
  exactos del spec §5 («Operativo», «En mantenimiento», «Fuera de
  servicio», «Retirado»); «Retirar» visible solo con el permiso.
- **Archivos afectados:** `templates/base.html`,
  `templates/registration/login.html`,
  `equipment/templates/equipment/*.html`.
- **Depende de:** T16.
- **Criterio de finalización:** interfaz coherente, íntegramente en
  español, sin textos quemados en inglés; comportamiento de permisos en
  plantillas correcto.
- **Pruebas / verificación:** suite completa en verde; aserciones de
  presencia de etiquetas clave añadidas a los tests de vistas
  existentes; revisión visual manual con `runserver` (checklist de los
  cuatro flujos).

### T18 — Django Admin (+tests)
- **Objetivo:** registrar `Equipment` en el Admin. `is_staff` habilita
  únicamente el acceso al sitio del Admin; para gestionar `Equipment`,
  el usuario debe poseer los permisos estándar correspondientes
  (`add/view/change_equipment`). El superusuario mantiene el bypass
  estándar de Django. `has_delete_permission()` → `False` y el guard
  `pre_delete` conservan el bloqueo de eliminación física para todos,
  incluido el superusuario (D4, plan §3.5); visualización de campos de
  auditoría.
- **Archivos afectados:** `equipment/admin.py`,
  `equipment/tests/test_admin.py`.
- **Depende de:** T17.
- **Criterio de finalización:** acceso al sitio Admin restringido a
  `is_staff`; la gestión de `Equipment` exige los permisos estándar;
  el superusuario conserva su bypass estándar salvo el borrado, que
  permanece bloqueado para cualquiera.
- **Pruebas / verificación** (`test_admin.py`): usuario `is_staff` sin
  permisos sobre `Equipment` no puede verlo ni gestionarlo en el Admin;
  staff con `view_equipment` accede al changelist y con
  `change_equipment` puede editar; superusuario accede íntegramente
  (bypass estándar); `has_delete_permission` es `False`; el intento de
  borrado individual y masivo vía Admin queda bloqueado, incluso para
  superusuario; campos de auditoría visibles. Suite en verde.

---

## Fase 5 — Cierre

### T19 — Verificación integral final
- **Objetivo:** validar la feature completa contra spec §9 y §10 antes
  de cerrar. Sin código nuevo de feature; ajustes menores solo si un
  chequeo falla (documentándolos).
- **Archivos afectados:** ninguno obligatorio; opcionalmente este
  documento (registro de resultados).
- **Depende de:** T18 (y, por transitividad, todas).
- **Criterio de finalización:** todos los ítems siguientes en verde.
- **Pruebas / verificación:**
  1. `pytest` completo en verde desde entorno limpio.
  2. `manage.py makemigrations --check --dry-run` limpio.
  3. Matriz spec §9 ↔ tests:

     | Grupo de criterios (§9) | Cobertura |
     |---|---|
     | Creación válida, requeridos, duplicado, estado inicial | `test_models`, `test_forms`, `test_views_create` |
     | Listado, búsqueda, filtro, retirados consultables | `test_views_list`, `test_views_search` |
     | Edición y unicidad al editar | `test_views_update`, `test_forms` |
     | Estados operativos permitidos / `retired` vetado a técnicos | `test_groups`, `test_permissions`, `test_views_update`, `test_views_retire` |
     | Retiro administrativo y conservación de datos | `test_views_retire` |
     | Ausencia total de borrado físico | `test_deletion`, `test_admin`, inspección de rutas/vistas |
     | Auditoría `created_*` / `updated_*` | `test_models`, `test_views_create`, `test_views_update` |
     | Administración vía `is_staff`/`is_superuser` | `test_admin`, `test_permissions` |

  4. Cruce spec §10 (19 tipos de prueba) ↔ archivos de la suite, sin
     huecos.
  5. Smoke punta a punta de los cuatro flujos de spec §7 con login
     real (cliente de pruebas autenticado y/o `runserver` manual
     documentado).
  6. `git status`: `db.sqlite3`, `db.sqlite3-journal`, `.env` y
     `.venv/` fuera del repositorio.
  7. Revisión de historial: commits en español, identificadores en
     inglés, un commit lógico por tarea.
