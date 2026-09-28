# Tareas retrospectivas: Mantenimientos (002-maintenance)

> **Carácter del documento:** inventario retrospectivo del trabajo ya presente;
> no constituye backlog aprobado. Trazabilidad asociada a
> [`spec.md`](spec.md). Los identificadores de tests son rutas existentes.

| ID | Trabajo documentado | Implementación / trazabilidad | Tests existentes | Estado |
|---|---|---|---|---|
| R01 | Modelos de registros, estados, auditoría y relación con equipos | `maintenance/models.py`, migraciones; `6b0d965`, `45dd76b` | `test_models.py`, `test_work_orders.py` | Implementado |
| R02 | Formularios, alta y edición con validación y permisos | `forms.py`, `views.py`, `urls.py`; `6b0d965`, `45dd76b`, `7b6024b` | `test_forms.py`, `test_views_create.py`, `test_views_update.py`, `test_permissions.py` | Implementado |
| R03 | Listado, detalle, búsqueda e historial | vistas y plantillas; `6b0d965` | `test_views_list.py`, `test_views_search.py`, `test_views_history.py` | Implementado |
| R04 | Orden de trabajo y numeración documental | `WorkOrder`, `DocumentSequence`; `45dd76b` | `test_work_orders.py` | Implementado |
| R05 | Aislamiento por organización | FK y filtros tenant; `c4ba7d7` | `test_views_list.py`, `test_views_search.py`, `test_views_history.py`, tests de creación/edición | Implementado |
| R06 | Validación de RUT | `maintenance/rut.py` y formularios; `47a00e7` | `test_rut.py`, `test_forms.py` | Implementado |
| R07 | Lecturas de medidor, planes y mantenimientos pendientes | `models.py`, `queries.py`, formularios y vistas; `b0baafb` | `test_models.py`, `test_pending.py`, `test_views_create.py` | Implementado |
| R08 | Restricción de borrado y administración | `signals.py`, `admin.py`; `6b0d965` y evolución posterior | `test_deletion.py`, `test_admin.py` | Implementado |

El estado “Implementado” describe la presencia histórica, no certifica por sí
mismo el resultado de una ejecución actual de la suite.
