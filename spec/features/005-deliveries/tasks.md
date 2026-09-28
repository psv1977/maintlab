# Tareas retrospectivas: Entregas (005-deliveries)

> **Carácter del documento:** trazabilidad retrospectiva del estado
> implementado, no backlog aprobado. Véase [`spec.md`](spec.md).

| ID | Trabajo documentado | Implementación / trazabilidad | Tests existentes | Estado |
|---|---|---|---|---|
| R01 | Modelo Delivery, estados, fechas y relaciones | `deliveries/models.py`, migraciones; `47a00e7` | `deliveries/tests/test_forms.py`, `test_views.py` | Implementado |
| R02 | Validación de formulario de entrega | `deliveries/forms.py`; `47a00e7` | `deliveries/tests/test_forms.py` | Implementado |
| R03 | Alta, listado, detalle y rutas | `deliveries/views.py`, `urls.py`, templates; `47a00e7` | `deliveries/tests/test_views.py` | Implementado |
| R04 | Permisos de técnicos | migración de permisos y vistas; `47a00e7` | `deliveries/tests/test_views.py` | Implementado |
| R05 | Organización y aislamiento tenant | FK/migración/filtros; `c4ba7d7` | `organizations/tests/test_isolation.py`, `deliveries/tests/test_views.py` | Implementado |
| R06 | Integración en navegación/dashboard | `dashboard/`, plantilla base; `474d8cc` | `dashboard/tests/test_views.py` | Implementado |

El estado expresa presencia en el repositorio; la ejecución actual se verifica
por separado durante la regularización.
