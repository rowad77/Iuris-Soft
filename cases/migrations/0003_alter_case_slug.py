# Generated by Django 5.1.6 on 2025-02-23 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0002_clientretainer_low_balance_notified_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="slug",
            field=models.SlugField(blank=True, editable=False, unique=True),
        ),
    ]
