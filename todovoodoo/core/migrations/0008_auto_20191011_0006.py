# Generated by Django 2.2.6 on 2019-10-11 07:06

import autoslug.fields
from django.db import migrations
import django_slugify_processor.text


class Migration(migrations.Migration):

    dependencies = [("core", "0007_station_slug")]

    operations = [
        migrations.AlterField(
            model_name="station",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                always_update=True,
                editable=False,
                populate_from="name",
                slugify=django_slugify_processor.text.slugify,
                unique=True,
            ),
        )
    ]