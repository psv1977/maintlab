# Tareas retrospectivas: Organizaciones (003-organizations)

> **Carácter del documento:** trazabilidad retrospectiva de implementación
> existente, no backlog aprobado. Véase [`spec.md`](spec.md).

| ID | Trabajo documentado | Implementación / trazabilidad | Tests existentes | Estado |
|---|---|---|---|---|
| R01 | Modelo Organization y datos de perfil | `organizations/models.py`, migraciones iniciales; `c4ba7d7` | `test_isolation.py`, `test_organization_registration.py` | Implementado |
| R02 | Asociación de membresía y resolución tenant | `tenant.py`, señales, middleware; `c4ba7d7` | `test_isolation.py`, `test_public_registration.py` | Implementado |
| R03 | Aislamiento de datos y escritura de solo lectura | `middleware.py`, filtros en apps consumidoras; `c4ba7d7`, `b0baafb` | `test_isolation.py`, tests de vistas de maintenance/equipment/deliveries | Implementado |
| R04 | Región, comuna y datos geográficos | modelos, migración y fixture; `cd341a9` | `test_organization_registration.py`, `test_isolation.py` | Implementado |
| R05 | Selector dinámico de comunas | endpoint/formulario y JavaScript/estáticos; `dfdc367` | `test_organization_registration.py` | Implementado |
| R06 | Estados de cuenta y período demo | modelo, migración, middleware y formularios; `c4ba7d7`, `b0baafb` | `test_isolation.py`, `test_organization_registration.py` | Implementado |
| R07 | Clientes por organización y unicidad de RUT | `Customer`, vistas y migración; `b0baafb` | `organizations/tests/test_customer.py`, `dashboard/tests/test_search.py` | Implementado |
| R08 | Invitaciones vinculadas a organización | modelos/vistas de organizations y users; `c4ba7d7` | `users/tests/test_public_registration.py` | Implementado |

La lista refleja cobertura localizada en la suite; no sustituye una ejecución
actual ni declara requisitos futuros.
