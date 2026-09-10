import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def assign_existing_users(apps, schema_editor):
    Organization = apps.get_model("organizations", "Organization")
    OrganizationMembership = apps.get_model("organizations", "OrganizationMembership")
    User = apps.get_model("auth", "User")
    organization, _ = Organization.objects.get_or_create(name="Empresa inicial")
    for user in User.objects.all():
        OrganizationMembership.objects.get_or_create(user=user, defaults={"organization": organization})


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "empresa", "verbose_name_plural": "empresas"},
        ),
        migrations.CreateModel(
            name="OrganizationMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="memberships", to="organizations.organization")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="organization_membership", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "asignación de empresa", "verbose_name_plural": "asignaciones de empresa"},
        ),
        migrations.RunPython(assign_existing_users, migrations.RunPython.noop),
    ]
