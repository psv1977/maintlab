# Tareas retrospectivas: Usuarios (004-users)

> **Carácter del documento:** inventario retrospectivo de trabajo ya
> implementado; no es un backlog nuevo. Véase [`spec.md`](spec.md).

| ID | Trabajo documentado | Implementación / trazabilidad | Tests existentes | Estado |
|---|---|---|---|---|
| R01 | Gestión interna de usuarios: alta, listado, detalle y edición | `users/views.py`, `forms.py`, templates; `6b0d965` | `users/tests/test_views.py`, `test_forms.py` | Implementado |
| R02 | Asignación de grupos y límites staff | formularios/vistas Django; `6b0d965`, `45dd76b` | `test_forms.py`, `test_views.py` | Implementado |
| R03 | Registro de organización y primer usuario | flujo público; `c4ba7d7`, `cd341a9` | `test_public_registration.py`, `test_organization_registration.py` | Implementado |
| R04 | Registro mediante invitación y asociación tenant | `OrganizationInvitation`, vistas; `c4ba7d7` | `test_public_registration.py` | Implementado |
| R05 | Usuario autenticado asignado automáticamente en formularios operativos | vistas/forms; `7b6024b` | `test_views_create.py` de equipment/maintenance | Implementado |
| R06 | Contraseñas y política/historial | validadores, señal y vista; `45dd76b` | `test_password_history.py`, `test_forms.py`, `test_views.py` | Implementado |
| R07 | Desactivación con protecciones | `UserDeactivateView`; `19a1026` | `users/tests/test_views.py` | Implementado |
| R08 | Geografía durante registro y carga dinámica | formularios/endpoint; `cd341a9`, `dfdc367` | `test_organization_registration.py` | Implementado |

“Implementado” identifica la funcionalidad existente y no implica una nueva
promesa de comportamiento o un resultado de tests no ejecutado.
