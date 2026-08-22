# Especificación: Gestión de equipos

## 1. Objetivo

Permitir registrar, consultar, buscar, editar y retirar equipos, conservando su información y preparando el sistema para asociar mantenimientos posteriormente.

## 2. Alcance

La feature incluye:

- Crear equipos.
- Consultar equipos mediante un listado.
- Buscar y filtrar equipos.
- Editar equipos.
- Cambiar el estado de un equipo a `retired`.
- Conservar la información de los equipos retirados.
- Registrar información de auditoría sobre creación y modificación.

Las interfaces se implementarán posteriormente con Django templates y forms.

## 3. Fuera de alcance

- Eliminación física de equipos.
- Registro o consulta de mantenimientos.
- Materiales e inventario.
- Adjuntos, fotografías o documentos.
- Importación y exportación masiva.
- API, DRF o SPA.

## 4. Datos del equipo

Cada equipo debe incluir:

| Campo | Identificador | Requerido | Reglas |
|---|---|---|---|
| Nombre | `name` | Sí | Describe el equipo de forma legible. |
| Código | `code` | Sí | Debe ser único. |
| Descripción | `description` | No | Información adicional del equipo. |
| Número de serie | `serial_number` | No | Identificador proporcionado por el fabricante. |
| Estado | `status` | Sí | Debe usar uno de los estados permitidos. |
| Usuario de creación | `created_by` | Sí | Usuario que registró el equipo. |
| Fecha de creación | `created_at` | Sí | Se registra automáticamente. |
| Usuario de modificación | `updated_by` | No | Vacío hasta la primera modificación. |
| Fecha de modificación | `updated_at` | No | Vacía hasta la primera modificación. |

Los identificadores de código, campos y estados deben mantenerse en inglés. La documentación y los textos visibles para usuarios estarán en español.

## 5. Estados

Los estados visibles son:

| Identificador interno | Texto visible |
|---|---|
| `operational` | Operativo |
| `in_maintenance` | En mantenimiento |
| `out_of_service` | Fuera de servicio |
| `retired` | Retirado |

Un equipo retirado se conserva en el sistema y no puede eliminarse físicamente.

## 6. Permisos

El grupo `tecnicos` puede:

- Crear equipos.
- Consultar equipos.
- Buscar equipos.
- Editar equipos.
- Cambiar el estado entre `operational`, `in_maintenance` y `out_of_service`.

El grupo `tecnicos` no puede:

- Cambiar un equipo al estado `retired`.
- Eliminar físicamente equipos.

La acción de retirar un equipo, es decir, cambiar su estado a `retired`, queda reservada a usuarios con permisos administrativos mediante `is_staff` o `is_superuser`.

No se crea un grupo `admin` ni un sistema RBAC personalizado. La definición de permisos debe mantenerse abierta para agregar o modificar grupos y permisos posteriormente.

## 7. Flujos funcionales

### 7.1 Crear equipo

1. El usuario autorizado abre el formulario de alta.
2. Completa los campos requeridos.
3. El sistema valida los datos.
4. El sistema rechaza códigos duplicados.
5. El sistema guarda el equipo con estado inicial `operational`.
6. El sistema registra el usuario y la fecha de creación.
7. El sistema actualiza el listado de equipos.

### 7.2 Consultar y buscar equipos

1. El usuario autorizado accede al listado.
2. El sistema muestra los equipos disponibles para consulta.
3. El usuario puede buscar por código, nombre o número de serie.
4. El usuario puede filtrar por estado.
5. Los equipos retirados permanecen consultables.

### 7.3 Editar equipo

1. El usuario autorizado selecciona un equipo.
2. Modifica los campos permitidos.
3. El sistema valida los datos.
4. El sistema impide asignar un código que ya pertenezca a otro equipo.
5. El sistema guarda los cambios.
6. El sistema registra el usuario y la fecha de modificación.

### 7.4 Retirar equipo

1. Un usuario administrativo autorizado selecciona un equipo.
2. Cambia su estado a `retired`.
3. El sistema conserva todos sus datos.
4. El equipo continúa disponible para consultas históricas.
5. Los usuarios del grupo `tecnicos` no pueden ejecutar esta acción.
6. No existe una operación de eliminación física.

## 8. Reglas de negocio

- `code` es obligatorio y único.
- `name` es obligatorio.
- `status` solo puede contener los valores definidos en esta especificación.
- Los nuevos equipos comienzan en estado `operational`.
- Los usuarios del grupo `tecnicos` solo pueden asignar los estados `operational`, `in_maintenance` y `out_of_service`.
- Solo la administración puede asignar el estado `retired`.
- Un equipo retirado no se elimina físicamente.
- Los equipos retirados conservan sus datos y siguen siendo consultables.
- `updated_by` permanece vacío hasta la primera modificación del equipo.
- `updated_at` también permanece vacío hasta la primera modificación del equipo.
- Cada modificación posterior actualiza `updated_by` y `updated_at`.
- La edición debe conservar la unicidad del código.
- Cada creación debe registrar `created_by` y `created_at`.
- La feature no debe depender de una aplicación de materiales o inventario.
- El diseño debe permitir asociar múltiples registros de mantenimiento a un equipo en una feature posterior.

## 9. Criterios de aceptación

- Un técnico puede crear un equipo válido.
- El sistema rechaza un equipo sin nombre.
- El sistema rechaza un equipo sin código.
- El sistema rechaza un código duplicado al crear.
- Un equipo nuevo queda en estado `Operativo`.
- Un equipo nuevo tiene `updated_by` vacío.
- Un equipo nuevo tiene `updated_at` vacío.
- Un técnico puede consultar el listado de equipos.
- Un técnico puede buscar por código, nombre y número de serie.
- Un técnico puede filtrar por estado.
- Un técnico puede editar un equipo.
- Un técnico puede cambiar un equipo entre `Operativo`, `En mantenimiento` y `Fuera de servicio`.
- Un técnico no puede cambiar un equipo al estado `Retirado`.
- Un usuario administrativo puede cambiar un equipo al estado `Retirado`.
- El sistema rechaza cambios que produzcan un código duplicado.
- Un técnico no puede eliminar físicamente un equipo.
- Un equipo retirado conserva sus datos y sigue siendo consultable.
- Un equipo nunca se elimina físicamente.
- La creación registra `created_by` y `created_at`.
- La primera modificación registra `updated_by` y `updated_at`.
- Cada modificación posterior actualiza `updated_by` y `updated_at`.
- La administración conserva sus capacidades mediante `is_staff` e `is_superuser`.

## 10. Pruebas requeridas

Cuando el proyecto Django y `pytest-django` estén configurados, deben existir pruebas para:

- Creación válida.
- Validación de campos requeridos.
- Unicidad del código.
- Estado inicial.
- Estados permitidos.
- Búsqueda por código, nombre y número de serie.
- Filtrado por estado.
- Edición válida.
- Rechazo de códigos duplicados durante la edición.
- Permitir al grupo `tecnicos` usar los estados operacionales.
- Rechazar al grupo `tecnicos` el cambio al estado `retired`.
- Permitir a usuarios administrativos cambiar al estado `retired`.
- Conservación de equipos retirados.
- Ausencia de eliminación física.
- Verificar que `updated_by` y `updated_at` están vacíos al crear.
- Verificar que ambos campos se completan en la primera modificación.
- Verificar que ambos campos se actualizan en modificaciones posteriores.
- Registro de `created_by` y `created_at`.
- Permisos del grupo `tecnicos`.
- Acceso administrativo mediante `is_staff` e `is_superuser`.
