# Generated by Django 2.2.6 on 2019-11-04 06:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [("core", "0009_auto_20191011_2242")]

    operations = [
        migrations.AddField(
            model_name="stationitem",
            name="item_type",
            field=models.TextField(
                choices=[("text", "Text"), ("boolean", "Boolean"), ("number", "Number")],
                default="text",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="reportentry",
            name="photo_upload",
            field=models.ImageField(
                help_text="Photo taken of the station.", null=True, upload_to="photos/%Y/%m/%d/"
            ),
        ),
        migrations.AlterField(
            model_name="reportentry",
            name="station",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.Station"
            ),
        ),
        migrations.CreateModel(
            name="ReportEntryText",
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
                ("instructions", models.TextField(blank=True)),
                ("data", models.TextField()),
                (
                    "report_entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportentrytext_items",
                        to="core.ReportEntry",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ReportEntryNumber",
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
                ("instructions", models.TextField(blank=True)),
                ("data", models.IntegerField()),
                (
                    "report_entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportentrynumber_items",
                        to="core.ReportEntry",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ReportEntryBoolean",
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
                ("instructions", models.TextField(blank=True)),
                ("data", models.BooleanField()),
                (
                    "report_entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportentryboolean_items",
                        to="core.ReportEntry",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
