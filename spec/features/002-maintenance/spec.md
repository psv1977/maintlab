# Especificación retroactiva: Mantenimientos (002-maintenance)

> **Carácter del documento:** especificación retroactiva del comportamiento
> existente en el repositorio. No es una autorización ni un plan para nuevas
> funcionalidades. La implementación histórica no se modifica con este
> documento.

## 1. Objetivo y alcance observado

La aplicación permite registrar y gestionar mantenimientos asociados a
equipos, consultar su historial y apoyar el seguimiento mediante órdenes de
trabajo, lecturas de medidor, planes y mantenimientos pendientes.

El alcance presente incluye:

- Crear, listar, consultar y editar registros de mantenimiento.
- Asociar registros a equipos y a la organización correspondiente.
- Registrar tipo, descripción, fechas, estado, responsable, notas y lectura de
  medidor; conservar auditoría de creación y modificación.
- Consultar historial por equipo y buscar o filtrar registros.
- Generar y relacionar órdenes de trabajo con secuencia documental.
- Definir planes por tiempo o por uso y calcular próximos servicios/vencimientos.
- Consultar planes y registros pendientes conforme a las consultas de dominio.
- Aplicar permisos Django al grupo `tecnicos` y mantener la protección contra
  eliminación física implementada para los registros.
- Usar RUT en los flujos que lo solicitan, con validación chilena.
- Restringir las consultas y operaciones al tenant/organización del usuario.

## 2. Reglas y límites observados

- `MaintenanceRecord` pertenece a un equipo y una organización; las referencias
  a equipo, orden y usuarios protegidas no se eliminan en cascada.
- Los estados del registro son `pending`, `in_progress` y `completed`; los tipos
  son `scheduled` y `unscheduled`.
- Los planes admiten estrategia por tiempo o por medidor y validan los campos
  requeridos para cada estrategia.
- Las operaciones permitidas a técnicos se determinan por permisos estándar y
  las asignaciones históricas del grupo `tecnicos`; esta especificación no
  introduce un RBAC nuevo.
- Dashboard y búsqueda universal se documentan en `006-dashboard-search`.
- Equipos, organizaciones, usuarios y entregas se detallan en sus propias
  features retroactivas.

## 3. Criterios observables

- Se puede crear, consultar y editar un registro válido ligado a un equipo.
- Se rechazan valores inválidos de formulario y RUT conforme a los validadores
  existentes.
- El historial y las búsquedas devuelven registros del ámbito autorizado.
- Se pueden crear y consultar órdenes de trabajo asociadas a equipos y registros.
- Los planes por tiempo y por medidor determinan sus siguientes servicios y
  vencimientos; los planes inactivos no se consideran vencidos.
- La consulta de pendientes utiliza las reglas temporales/de medidor existentes.
- La auditoría se completa en los flujos implementados y la eliminación física
  está cubierta por la protección existente.

## 4. Implementación, commits y tests de referencia

Implementación principal: `maintenance/models.py`, `forms.py`, `views.py`,
`queries.py`, `signals.py`, `admin.py`, `urls.py`, `migrations/` y
`templates/maintenance/`.

Commits principales: `6b0d965` (app, registros e historial), `45dd76b` (órdenes
de trabajo y ampliación de modelo), `47a00e7` (validación RUT), `c4ba7d7`
(aislamiento por organización), `b0baafb` (planes, lecturas y pendientes), y
`7b6024b` (asignación automática del usuario autenticado).

Tests existentes: `maintenance/tests/test_models.py`, `test_forms.py`,
`test_permissions.py`, `test_deletion.py`, `test_views_create.py`,
`test_views_list.py`, `test_views_history.py`, `test_views_search.py`,
`test_views_update.py`, `test_work_orders.py`, `test_pending.py`, `test_rut.py`
y `test_admin.py`.
