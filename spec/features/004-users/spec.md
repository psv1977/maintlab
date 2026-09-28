# Especificación retroactiva: Usuarios (004-users)

> **Carácter del documento:** especificación retroactiva del comportamiento
> actual de gestión y registro de usuarios. No crea una arquitectura de roles
> distinta del modelo estándar de Django ni autoriza nuevas funciones.

## 1. Objetivo y alcance observado

La aplicación permite administrar usuarios dentro de la organización,
registrar organizaciones y usuarios iniciales, incorporar usuarios mediante
invitación y realizar operaciones de gestión de acceso.

- Listar, consultar, crear y editar usuarios para personal autorizado.
- Asignar grupos Django; reservar la gestión de capacidades staff a
  superusuarios según formularios existentes.
- Cambiar contraseñas desde la interfaz administrativa y conservar el
  historial/validación implementado.
- Desactivar usuarios con confirmación y protecciones para impedir
  auto-desactivación, desactivar el último superusuario activo o que un staff
  ordinario desactive a otro administrador.
- Iniciar registro público identificando organización por RUT; crear una
  organización demo y su primer usuario o registrarse mediante invitación.
- Asociar cada usuario a su organización y autenticarse al terminar el flujo.
- Seleccionar región/comuna en registro y usar carga dinámica de comunas.

## 2. Reglas y límites observados

- Se utiliza `django.contrib.auth.models.User`; no hay modelo RBAC propio.
- El acceso a la gestión interna requiere `is_staff`; el superusuario posee las
  capacidades administrativas estándar.
- Los usuarios no superusuarios quedan limitados a su organización.
- El primer usuario registrado para una nueva organización se marca `is_staff`
  conforme al flujo actual; las invitaciones tienen expiración, revocación y
  uso único conforme al estado del modelo.
- Gestión de organizaciones y multi-tenancy se amplía en `003-organizations`.

## 3. Criterios observables

- Personal autorizado puede gestionar usuarios dentro de su tenant.
- El usuario no puede consultar/editar usuarios de otro tenant mediante las
  vistas protegidas.
- Los formularios aplican validación de identidad, contraseña y grupos.
- El registro distingue primer usuario y registro por invitación, asocia tenant
  y completa autenticación.
- La desactivación respeta las restricciones de seguridad descritas.
- La gestión de contraseñas aplica las reglas e historial implementados.

## 4. Implementación, commits y tests de referencia

Implementación: `users/models.py`, `forms.py`, `views.py`, `urls.py`,
`signals.py`, `password_validators.py`, `templates/users/` y migraciones.

Commits principales: `6b0d965` (app y gestión básica), `45dd76b` (validación e
historial de contraseñas), `c4ba7d7` (registro seguro/invitaciones), `cd341a9`
(geografía de registro), `dfdc367` (comunas dinámicas), `7b6024b` (usuario
autenticado automáticamente), `19a1026` (desactivación segura) y `2442856`
(ajuste del registro público).

Tests existentes: `users/tests/test_forms.py`, `test_views.py`,
`test_public_registration.py`, `test_organization_registration.py` y
`test_password_history.py`.
