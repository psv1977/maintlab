from django.db import migrations


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    group, _ = Group.objects.get_or_create(name="tecnicos")
    permissions = Permission.objects.filter(
        content_type__app_label="deliveries",
        content_type__model="delivery",
        codename__in=["add_delivery", "view_delivery", "change_delivery"],
    )
    group.permissions.add(*permissions)


class Migration(migrations.Migration):
    dependencies = [("deliveries", "0001_initial")]

    operations = [migrations.RunPython(assign_permissions, migrations.RunPython.noop)]
