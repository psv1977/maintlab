# Especificación retroactiva: Organizaciones (003-organizations)

> **Carácter del documento:** especificación retroactiva de funcionalidad ya
> existente; no representa alcance nuevo ni un plan de implementación.

## 1. Objetivo y alcance observado

El sistema agrupa usuarios y datos operativos por organización, restringiendo
la consulta y modificación al tenant asociado. Incluye administración de
organizaciones, clientes, membresías e invitaciones, estado de cuenta y
clasificación geográfica chilena.

- Organización con nombre, RUT, giro, dirección, región, comuna y estado de
  cuenta (`active`, `demo`, `read_only`, `suspended`).
- Estados demo y sus fechas; lectura restringida cuando vence demo o
  suscripción, o cuando la cuenta está en solo lectura/suspendida.
- Clientes por organización, identificados por RUT único dentro de ella.
- Asociación usuario-organización y resolución del tenant para vistas.
- Invitaciones vinculadas a organización, con expiración, uso y revocación.
- Regiones y comunas cargadas desde datos geográficos; selector dinámico de
  comunas al registrar organización.
- Middleware, filtros y restricciones de escritura para aislamiento y modo de
  solo lectura.

## 2. Reglas y límites observados

- Los datos de dominio incluyen una organización y las vistas deben filtrar por
  la organización del usuario autenticado.
- El RUT de organización es único cuando está presente; el RUT de cliente es
  único por organización.
- La invitación solo es utilizable si no expiró, no fue revocada ni utilizada.
- La clasificación de regiones y comunas y su integridad referencial la
  administra la aplicación `organizations`.
- El alta de organización y usuarios pertenece a `004-users`; búsqueda de
  clientes pertenece a `006-dashboard-search`.

## 3. Criterios observables

- Los usuarios ordinarios no consultan ni modifican datos de otra organización.
- Las vistas de clientes y los flujos de registro preservan la organización.
- Organizaciones demo vencidas, suspendidas o en solo lectura no admiten las
  operaciones de escritura bloqueadas por middleware.
- Regiones y comunas válidas aparecen en formularios y la selección dinámica
  devuelve comunas de la región solicitada.
- La membresía y las invitaciones permanecen asociadas a una organización.

## 4. Implementación, commits y tests de referencia

Implementación: `organizations/models.py`, `tenant.py`, `middleware.py`,
`signals.py`, `rut.py`, `forms.py`, `views.py`, `admin.py`, `migrations/` y
`fixtures/chile_geography.json`.

Commits principales: `c4ba7d7` (registro seguro y aislamiento), `cd341a9`
(región/comuna), `dfdc367` (selector dinámico), `b0baafb` (clientes y
aislamiento relacionado con búsqueda) y `2442856` (ajuste de registro público).

Tests existentes: `organizations/tests/test_customer.py`,
`organizations/tests/test_isolation.py`, `users/tests/test_organization_registration.py`
y `users/tests/test_public_registration.py`.
