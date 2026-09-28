# Especificación retroactiva: Entregas (005-deliveries)

> **Carácter del documento:** especificación retroactiva de la aplicación
> existente; no añade requisitos nuevos.

## 1. Objetivo y alcance observado

La aplicación registra entregas y recepciones de equipos asociados a clientes,
con consulta del historial operativo y vinculación opcional a una orden de
trabajo.

- Crear, listar y consultar entregas.
- Registrar equipo, cliente y RUT, responsable de entrega, receptor, fecha de
  entrega/recepción, estado y notas.
- Asociar opcionalmente una entrega a una orden de trabajo.
- Mantener el tenant de organización y las relaciones protegidas con equipo,
  orden y usuarios.
- Aplicar formularios, rutas, permisos de técnicos y presentación Django.

Los estados existentes son `pending`, `delivered` y `returned` (etiquetas
visibles «Pendiente», «Entregado» y «Recibido»). La aplicación no documenta
eliminación física como flujo funcional.

## 2. Criterios observables

- Un usuario autorizado puede crear una entrega con datos válidos.
- Los campos requeridos y valores admitidos se validan mediante el formulario.
- Los usuarios pueden consultar el listado y detalle permitidos.
- La entrega permanece asociada a la organización, equipo y, si fue indicado,
  orden de trabajo correspondientes.
- La fecha de actualización se mantiene según el modelo existente.

## 3. Implementación, commits y tests de referencia

Implementación: `deliveries/models.py`, `forms.py`, `views.py`, `urls.py`,
`admin.py`, `migrations/` y `templates/deliveries/`.

Commits principales: `47a00e7` (aplicación y flujos de entrega), `474d8cc`
(dashboard e integración), y `c4ba7d7` (asociación/aislamiento por
organización).

Tests existentes: `deliveries/tests/test_forms.py` y
`deliveries/tests/test_views.py`; los tests de aislamiento de
`organizations/tests/test_isolation.py` verifican el contexto multi-tenant
transversal cuando corresponde.
