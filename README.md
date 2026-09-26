# maintlab

Aplicación Django para gestionar equipos, mantenimientos, usuarios y empresas.

## Ejecutar en desarrollo

Desde la raíz del proyecto, activa el entorno virtual y prepara la base de datos:

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

La aplicación estará disponible en <http://127.0.0.1:8000/>. Para acceder, usa
una cuenta existente o registra una empresa y su primer usuario desde
<http://127.0.0.1:8000/users/register/>.

## Cargar equipos de muestra

El archivo `equipment/fixtures/equipment_sample.csv` contiene 50 equipos y se
carga desde la pantalla de importación; no se carga automáticamente con
`loaddata`.

1. Inicia sesión con un usuario `is_staff` que pertenezca a la empresa donde
   quieres cargar los equipos. Si acabas de registrar el usuario de prueba,
   puedes habilitarle el acceso a la importación desde la raíz del proyecto:

   ```bash
   python manage.py shell -c "from django.contrib.auth.models import User; user = User.objects.get(username='USUARIO'); user.is_staff = True; user.save(update_fields=['is_staff'])"
   ```

   Sustituye `USUARIO` por el nombre de usuario correspondiente.

2. Vuelve a iniciar sesión y abre <http://127.0.0.1:8000/equipment/import/>.
3. Selecciona `equipment/fixtures/equipment_sample.csv` y pulsa **Validar e
   importar**. La pantalla debe confirmar que se importaron 50 equipos.

Los códigos del archivo son únicos. La importación rechaza filas cuyos códigos
ya existan en esa empresa; por eso, para repetir la prueba, usa una empresa de
prueba nueva o prepara datos limpios de esa empresa.

## Pruebas

```bash
pytest
```
