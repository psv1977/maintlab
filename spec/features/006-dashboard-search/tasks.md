# Tareas retrospectivas: Dashboard y búsqueda universal (006-dashboard-search)

> **Carácter del documento:** trazabilidad retrospectiva de la funcionalidad
> presente; no es backlog para trabajo futuro. Véase [`spec.md`](spec.md).

| ID | Trabajo documentado | Implementación / trazabilidad | Tests existentes | Estado |
|---|---|---|---|---|
| R01 | Página principal y protección por autenticación | `DashboardView`, URLs y plantilla; `474d8cc` | `dashboard/tests/test_views.py` | Implementado |
| R02 | Métricas de equipos, mantenimientos y órdenes | `dashboard/views.py`; `474d8cc` | `dashboard/tests/test_views.py` | Implementado |
| R03 | Recientes y próximos mantenimientos | `DashboardView`; `474d8cc` | `dashboard/tests/test_views.py` | Implementado |
| R04 | Búsqueda universal de clientes por nombre/RUT | `UniversalSearchView`; `b0baafb`, `2442856` | `dashboard/tests/test_search.py`, `organizations/tests/test_customer.py` | Implementado |
| R05 | Búsqueda universal de equipos y relaciones/identificadores | anotaciones y filtros; `b0baafb` | `dashboard/tests/test_search.py`, `equipment/tests/test_identifiers.py`, `test_new_fields.py` | Implementado |
| R06 | Aislamiento por tenant y ausencia de duplicados | filtros por organización y `distinct()`; `b0baafb`, con base en `c4ba7d7` | `dashboard/tests/test_search.py`, `organizations/tests/test_isolation.py` | Implementado |
| R07 | Integración de búsqueda con navegación y registro público | URLs/templates; `b0baafb`, `2442856` | `dashboard/tests/test_search.py`, `users/tests/test_public_registration.py` | Implementado |

Los IDs son una organización retrospectiva, no la numeración de tareas de un
plan de build. No se crea `plan.md` para esta feature.
