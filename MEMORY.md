# MEMORY.md — MaintLab

## Propósito

Este archivo contiene contexto persistente y resumido del proyecto MaintLab.
No reemplaza AGENTS.md, las especificaciones SDD ni el código.

Fuentes de verdad:
- AGENTS.md: reglas de trabajo y restricciones del proyecto.
- spec/features/: especificaciones funcionales y trazabilidad.
- Código y tests: implementación actual.
- MEMORY.md: contexto resumido y decisiones relevantes entre sesiones.

## Estado actual

MaintLab es una aplicación Django para gestión de mantenimiento.

Features documentadas:
- 001-equipment
- 002-maintenance
- 003-organizations
- 004-users
- 005-deliveries
- 006-dashboard-search

Las features 002–006 fueron documentadas retroactivamente.
A partir de la siguiente feature nueva se utilizará SDD antes de implementar:

spec.md → plan.md → tasks.md → implementación → tests → validación.

## Decisiones vigentes

### Equipos
- Los equipos no se eliminan físicamente como operación normal.
- El retiro conserva el registro y su historial.
- El retiro individual se autoriza mediante el permiso `retire_equipment`; no exige `is_staff`.
- La importación masiva admite CSV/XLSX.
- La importación masiva es una operación administrativa.
- Provisionalmente se utiliza `is_staff` para autorizarla.
- El modelo definitivo de roles administrativos está pendiente de diseño.

### Operaciones masivas
- No permitir eliminación física masiva ordinaria.
- Cualquier operación masiva debe priorizar seguridad, validación y trazabilidad.
- El eventual retiro masivo requiere diseño específico antes de implementarse.

## Hallazgos funcionales pendientes

- Revisar el comportamiento 403 de Deliveries.
- Probar manualmente la importación masiva de equipos.
- Evaluar MaintLab mediante uso real antes de definir la siguiente feature.

## Validación conocida

- Suite: 246 tests aprobados en la última ejecución registrada; la suite completa no pudo recolectarse en una verificación posterior porque faltaba `openpyxl` (`spec/features/001-equipment/tasks.md`).
- `python manage.py check`: sin errores.
- `makemigrations --check --dry-run`: sin cambios pendientes.

## Próximo paso

Continuar la revisión funcional manual de MaintLab.
No definir automáticamente una nueva feature hasta identificar una necesidad funcional real.

## Regla de mantenimiento de este archivo

Actualizar MEMORY.md únicamente cuando una decisión o estado sea útil para
futuras sesiones.

No copiar aquí specs completas, listas de tareas, código ni historial detallado
de commits.
