import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("equipment", "0004_location_equipment_application_equipment_brand_and_more"),
        ("maintenance", "0003_documentsequence_maintenancerecord_completed_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Delivery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("client_name", models.CharField(max_length=200)),
                ("client_rut", models.CharField(db_index=True, max_length=20)),
                ("received_by", models.CharField(max_length=200)),
                ("delivered_at", models.DateTimeField()),
                ("returned_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("pending", "Pendiente"), ("delivered", "Entregado"), ("returned", "Recibido")], default="pending", max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="deliveries_created", to=settings.AUTH_USER_MODEL)),
                ("delivered_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="deliveries_made", to=settings.AUTH_USER_MODEL)),
                ("equipment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="deliveries", to="equipment.equipment")),
                ("work_order", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="deliveries", to="maintenance.workorder")),
            ],
            options={"verbose_name": "entrega", "verbose_name_plural": "entregas", "ordering": ["-delivered_at"]},
        ),
    ]
