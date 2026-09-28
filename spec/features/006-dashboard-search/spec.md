# Especificación retroactiva: Dashboard y búsqueda universal (006-dashboard-search)

> **Carácter del documento:** especificación retroactiva de las pantallas y
> búsquedas ya implementadas; no amplía el alcance de otras features.

## 1. Objetivo y alcance observado

Proporcionar una página inicial autenticada con un resumen operativo del tenant
y una búsqueda universal de equipos y clientes de la organización del usuario.

### Dashboard

- Mostrar cantidades de mantenimientos abiertos y planes vencidos.
- Mostrar equipos y mantenimientos por estado y total de órdenes de trabajo.
- Presentar equipos y mantenimientos recientes y próximos mantenimientos en la
  ventana temporal implementada.
- Todas las métricas y listas se limitan a la organización resuelta para el
  usuario autenticado.

### Búsqueda universal

- Buscar clientes por nombre y RUT normalizado.
- Buscar equipos por nombre, código, número de serie, marca, modelo,
  aplicación, ubicación, cliente/RUT asociado e identificadores.
- Presentar resultados separados por tipo, sin duplicar equipos cuando varias
  relaciones coinciden.
- Limitar resultados al tenant y requerir autenticación.
- La búsqueda local en el listado de equipos definida por `001-equipment`
  permanece distinta; su extensión universal se registra aquí.

## 2. Criterios observables

- Un usuario anónimo es enviado al flujo de autenticación.
- El dashboard presenta el resumen de su organización y no mezcla datos de
  otras organizaciones.
- La búsqueda vacía no devuelve resultados; una consulta encuentra coincidencias
  en los campos definidos.
- RUT puede buscarse con puntuación o sin ella conforme a la normalización
  implementada.
- Equipos y clientes devueltos pertenecen al tenant; la búsqueda de equipo
  maneja coincidencias relacionales sin duplicados.

## 3. Implementación, commits y tests de referencia

Implementación: `dashboard/views.py`, `urls.py`,
`templates/dashboard/index.html`, `search_results.html`, configuración de URLs
y navegación global.

Commits principales: `474d8cc` (dashboard), `b0baafb` (búsqueda universal e
integración con clientes/equipos) y `2442856` (ajuste adicional de búsqueda y
registro público).

Tests existentes: `dashboard/tests/test_views.py`,
`dashboard/tests/test_search.py`, con cobertura complementaria de campos de
equipo/clientes en `equipment/tests/test_identifiers.py`,
`equipment/tests/test_new_fields.py`, `organizations/tests/test_customer.py`
y `users/tests/test_public_registration.py`.
