# Generated by Django 2.2.5 on 2019-09-28 07:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0005_station_refund_value"),
    ]

    operations = [
        migrations.AlterUniqueTogether(name="station", unique_together={("owner", "name")}),
        migrations.CreateModel(
            name="StationItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                ("pub_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of what to include in a report entry. (e.g. 'take a picture of the towels')'",
                    ),
                ),
                (
                    "station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.Station"
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
