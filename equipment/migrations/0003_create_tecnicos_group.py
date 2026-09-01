from django.db import migrations


GROUP_NAME = "tecnicos"
PERMISSIONS = {
    "add_equipment": "Can add equipment",
    "view_equipment": "Can view equipment",
    "change_equipment": "Can change equipment",
}


def create_tecnicos_group(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="equipment",
        model="equipment",
    )
    permissions = []
    for codename, name in PERMISSIONS.items():
        permission, _ = Permission.objects.get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={"name": name},
        )
        permissions.append(permission)

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    group.permissions.set(permissions)


def remove_tecnicos_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=GROUP_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("equipment", "0002_alter_equipment_options"),
    ]

    operations = [
        migrations.RunPython(create_tecnicos_group, remove_tecnicos_group),
    ]
