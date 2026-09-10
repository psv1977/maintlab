# Migración para agregar geografía (Región y Comuna) a Organization

from django.db import migrations, models
import django.db.models.deletion


def load_geography_data(apps, schema_editor):
    import json
    import os

    Region = apps.get_model("organizations", "Region")
    Comuna = apps.get_model("organizations", "Comuna")

    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "organizations",
        "fixtures",
        "chile_geography.json",
    )

    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)

    regions_map = {}
    for item in data:
        if item["model"] == "organizations.region":
            r = Region(pk=item["pk"], name=item["fields"]["name"])
            r.save()
            regions_map[item["pk"]] = r

    for item in data:
        if item["model"] == "organizations.comuna":
            region = regions_map[item["fields"]["region"]]
            Comuna(pk=item["pk"], region=region, name=item["fields"]["name"]).save()

    Organization = apps.get_model("organizations", "Organization")
    default_region = Region.objects.first()
    default_comuna = Comuna.objects.filter(region=default_region).first()
    if default_region and default_comuna:
        for org in Organization.objects.all():
            org.region = default_region
            org.comuna = default_comuna
            org.save(update_fields=["region", "comuna"])


def reverse_load_geography_data(apps, schema_editor):
    Comuna = apps.get_model("organizations", "Comuna")
    Region = apps.get_model("organizations", "Region")
    Comuna.objects.all().delete()
    Region.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0003_alter_organization_rut"),
    ]

    operations = [
        migrations.CreateModel(
            name="Region",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "verbose_name": "región",
                "verbose_name_plural": "regiones",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Comuna",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="comunas",
                        to="organizations.region",
                    ),
                ),
            ],
            options={
                "verbose_name": "comuna",
                "verbose_name_plural": "comunas",
                "ordering": ["name"],
                "unique_together": {("region", "name")},
            },
        ),
        migrations.AddField(
            model_name="organization",
            name="region",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="organizations.region",
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="comuna",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="organizations.comuna",
            ),
        ),
        migrations.RunPython(
            load_geography_data,
            reverse_load_geography_data,
        ),
        migrations.AlterField(
            model_name="organization",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="organizations.region",
            ),
        ),
        migrations.AlterField(
            model_name="organization",
            name="comuna",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="organizations.comuna",
            ),
        ),
    ]
