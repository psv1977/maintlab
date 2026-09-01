from django.db import migrations


GROUP_NAME = "tecnicos"
MAINTENANCE_PERMISSIONS = {
    "add_maintenance": "Can add maintenance record",
    "view_maintenance": "Can view maintenance record",
    "change_maintenance": "Can change maintenance record",
}


def add_maintenance_permissions_to_tecnicos(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="maintenance",
        model="maintenancerecord",
    )
    permissions = []
    for codename, name in MAINTENANCE_PERMISSIONS.items():
        permission, _ = Permission.objects.get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={"name": name},
        )
        permissions.append(permission)

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    group.permissions.add(*permissions)


def remove_maintenance_permissions_from_tecnicos(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="maintenance",
        model="maintenancerecord",
    )
    codenames = list(MAINTENANCE_PERMISSIONS.keys())
    permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=codenames,
    )
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    group.permissions.remove(*permissions)


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0001_initial"),
        ("equipment", "0003_create_tecnicos_group"),
    ]

    operations = [
        migrations.RunPython(
            add_maintenance_permissions_to_tecnicos,
            remove_maintenance_permissions_from_tecnicos,
        ),
    ]
