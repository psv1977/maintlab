# Plan: Gestión de equipos (001-equipment)

Plan técnico derivado de `spec.md` y de las restricciones globales de
`AGENTS.md`. Código, identificadores, modelos y migraciones en inglés;
documentación, docstrings, commits y textos visibles en español.

## 1. Alcance técnico

Implementar la feature completa en Django (MVT, sin DRF ni SPA):

- App `equipment` como única app nueva del MVP en esta fase.
- Modelo `Equipment` con auditoría (`created_by`, `created_at`,
  `updated_by`, `updated_at`).
- Permisos estándar de Django más el permiso personalizado
  `retire_equipment`.
- Grupo `tecnicos` creado por migración de datos idempotente.
- Bloqueo de eliminación física a nivel modelo (fuera de la UI).
- Gestión de alta, consulta y edición, con búsqueda/filtrado, retiro
  restringido y plantillas en español, sin eliminación física.
- Suite de pruebas incrementales con `pytest` + `pytest-django`.

Fuera de alcance (según spec §3): mantenimientos, materiales, inventario,
adjuntos, importación/exportación masiva, API.

## 2. Decisiones de diseño resueltas

| ID | Decisión | Resolución |
|----|----------|------------|
| D1 | Instalación de dependencias | Autorizada; se ejecuta al pasar Plan → Build |
| D2 | Entorno | Recrear `.venv` con **Python 3.13.15** y **Django 5.2 LTS**, buscando paridad con el entorno de despliegue; el **Python 3.14.4 de Ubuntu permanece intacto** |
| D3 | `on_delete` de `created_by`/`updated_by` | `PROTECT` |
| D4 | Eliminación física | Bloqueada también fuera de la UI (nivel modelo) |
| D5 | Grupo `tecnicos` | Migración de datos idempotente |
| D6 | Retiro | Solo permiso `retire_equipment`; no exigir `is_staff` |
| D7 | Login | Incluir temporalmente `django.contrib.auth.urls` |
| D8 | Paginación | 20 equipos por página |
| D9 | Zona horaria | `TIME_ZONE = "America/Santiago"` |
| D10 | Longitudes de campos | `name` 200 · `code` 50 · `serial_number` 100 · `description` TextField (sin límite) |
| D11 | Plantillas globales | `templates/base.html` en la raíz del proyecto |

No quedan decisiones abiertas para esta feature.

## 3. Diseño

### 3.1 Estructura de archivos prevista

```
maintlab/            # paquete del proyecto (settings, urls, wsgi, asgi)
equipment/           # app MVP
    migrations/
    tests/           # paquete de pruebas pytest
    templates/equipment/   # plantillas propias del app
templates/           # plantillas globales compartidas
    base.html
manage.py
pytest.ini
requirements.txt
spec/
```

Convención: plantillas globales compartidas en `templates/` (raíz);
plantillas propias del app en `equipment/templates/equipment/`.

### 3.2 Configuración base (`maintlab/settings.py`)

- `LANGUAGE_CODE = "es"`, `USE_TZ = True`,
  `TIME_ZONE = "America/Santiago"` (D9).
- `TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]` (D11).
- `LOGIN_URL` apuntando al login de `django.contrib.auth.urls`
  (inclusión temporal, D7).

### 3.3 Modelo `Equipment`

| Campo | Tipo | Reglas |
|---|---|---|
| `name` | CharField | obligatorio, `max_length=200` (D10) |
| `code` | CharField | obligatorio, único, `max_length=50` (D10) |
| `description` | TextField | opcional (`blank=True`) |
| `serial_number` | CharField | opcional, `max_length=100` (D10) |
| `status` | TextChoices | `operational` \| `in_maintenance` \| `out_of_service` \| `retired`; etiquetas visibles en español; default `operational` |
| `created_by` | FK `User` | obligatoria, `on_delete=PROTECT` (D3) |
| `created_at` | DateTimeField | `auto_now_add=True` |
| `updated_by` | FK `User` | nula hasta primera edición, `on_delete=PROTECT` (D3) |
| `updated_at` | DateTimeField | nula hasta primera edición; asignación manual en vistas (**sin** `auto_now`) |

Incluye `__str__` y `Meta.ordering`.

### 3.4 Permisos y roles

- Permisos por defecto de Django conservados:
  `add_equipment`, `change_equipment`, `view_equipment`,
  `delete_equipment`.
- Permiso personalizado en `Meta.permissions`:
  `retire_equipment` («Can retire equipment»).
- Grupo `tecnicos`: exactamente `add/view/change_equipment`;
  nunca `delete_equipment` ni `retire_equipment` (migración de datos
  idempotente, D5). Sin grupos personalizados adicionales; la
  administración usa `is_staff`/`is_superuser` (AGENTS.md).
- El retiro se autoriza **solo** por `retire_equipment`
  (PermissionRequiredMixin); el superusuario pasa implícitamente;
  no se exige `is_staff` (D6).

### 3.5 Integridad: sin eliminación física (D4)

- Guard `pre_delete` sobre `Equipment` que impide el borrado,
  cubriendo tanto `instance.delete()` como `queryset.delete()`
  (borrado masivo incluido el del Admin).
- Complementos de superficie: sin rutas ni acciones de borrado en
  vistas, `has_delete_permission()` → `False` en el Admin.

### 3.6 Auditoría

- Alta: `form_valid` de CreateView asigna `created_by`; `created_at`
  es automático.
- Edición: `form_valid` de UpdateView asigna `updated_by` y
  `updated_at` en cada guardado (manual, no `auto_now`, para respetar
  «vacío hasta la primera modificación»).
- Los técnicos no pueden asignar `status = retired` ni siquiera
  manipulando el POST: el formulario limita choices y la vista lo
  refuerza en servidor.

### 3.7 URLs y vistas

Namespace `app_name = "equipment"` bajo `/equipment/`, con rutas
nombradas:

| Ruta | Vista | Protección |
|---|---|---|
| `list` | ListView (`paginate_by = 20`, D8) | LoginRequired |
| `detail` | DetailView | LoginRequired |
| `create` | CreateView | LoginRequired |
| `update` | UpdateView | LoginRequired |
| `retire` | Acción dedicada POST con confirmación | Permiso `retire_equipment` (D6) |

Búsqueda y filtro en el listado: parámetro GET `q` con `icontains`
OR sobre `code`, `name`, `serial_number`; parámetro `status` exacto;
ambos combinables; estado inválido ignorado; retirados siempre
consultables.

### 3.8 Plantillas

- Globales: `templates/base.html` (D11).
- Del app: `equipment_list.html`, `equipment_detail.html`,
  `equipment_form.html`, `equipment_confirm_retire.html`.
- Textos visibles y etiquetas de estado según spec §5, en español.
- Botón/acción «Retirar» visible solo para quien tenga
  `retire_equipment`.

## 4. Hoja de ruta por fases (backlog acordado T01–T19)

> Nota: `tasks.md` aún no existe; se materializará completo, con las
> tareas T01–T19, antes de iniciar Build (no progresivamente por fases).
> La numeración siguiente es la acordada, con **T19 como verificación
> integral**.

1. **Infraestructura** — T01 entorno Python 3.13 + dependencias
   (solo al iniciar Build), T02 proyecto base, T03 pytest-django.
2. **Dominio, permisos e integridad** — T04 app `equipment`,
   T05 modelo (+tests), T06 migraciones, T07 permisos y
   `retire_equipment` (+tests), T08 bloqueo de borrado fuera de la UI
   (+tests), T09 grupo `tecnicos` por migración de datos (+tests).
3. **Formulario, URLs y vistas** — T10 `EquipmentForm` (+tests),
   T11 estructura de URLs, T12 listado/detalle + login temporal +
   paginación (+tests), T13 búsqueda icontains y filtro por estado
   (+tests), T14 alta con auditoría (+tests), T15 edición con
   auditoría y estados permitidos (+tests), T16 retiro autorizado
   (+tests).
4. **Interfaz y administración** — T17 plantillas consistentes en
   español, T18 Django Admin (+tests).
5. **Cierre** — T19 verificación integral.

Cada tarea incorpora sus propios tests y cierra en verde antes de
pasar a la siguiente.

## 5. Estrategia de pruebas

- Ejecutor: `pytest` con `pytest-django`; BD de pruebas SQLite en
  memoria configurada desde T03.
- Distribución incremental por tarea, en `equipment/tests/`:
  `test_models.py`, `test_permissions.py`, `test_deletion.py`,
  `test_groups.py`, `test_forms.py`, `test_views_list.py`,
  `test_views_search.py`, `test_views_create.py`,
  `test_views_update.py`, `test_views_retire.py`, `test_admin.py`.
- Verificación integral (T19): cruce checklist de aceptación §9 ↔
  tests y pruebas requeridas §10 ↔ tests; smoke punta a punta de los
  cuatro flujos de spec §7 con login real; ausencia total de caminos
  de borrado; `db.sqlite3` fuera del repositorio.

## 6. Restricciones y riesgos

| Riesgo / restricción | Mitigación |
|---|---|
| `.venv/`, `.env`, `db.sqlite3`, `db.sqlite3-journal` son estado local | Nunca versionados ni modificados salvo T01 (recreación de `.venv` ya autorizada, D1/D2) |
| SQLite durante todo el MVP | Sin migraciones fuera de SQLite; sin cambio de motor |
| `updated_*` depende de asignación manual | Tests específicos: vacío al crear, completo en 1.ª edición, refrescado en posteriores |
| Borrado programático podría saltarse la UI | Guard `pre_delete` cubre instancia y queryset; tests de T08/T18 |
| Acoplamiento con futuras apps (mantenimientos, inventario) | Modelo extensible (FK futura desde mantenimientos hacia `Equipment`), sin referencias inversas creadas ahora; sin apps post-MVP creadas |
| Dependencias sin instalar todavía | Nada se instala hasta la orden expresa de pasar Plan → Build (T01) |

## 7. Criterios de completitud de la feature

- Todos los criterios de aceptación de spec §9 cubiertos por tests en verde.
- Suite `pytest` íntegra y `makemigrations --check` limpio.
- Cuatro flujos funcionales (§7) operativos end-to-end.
- Sin rutas, vistas ni acciones de eliminación física.
- Documentación y commits en español; código e identificadores en inglés.
