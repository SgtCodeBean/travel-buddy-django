# Generated by Django 5.1.7 on 2025-04-28 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0006_alter_itinerary_budget"),
    ]

    operations = [
        migrations.RenameField(
            model_name="itinerary",
            old_name="user",
            new_name="author",
        ),
    ]
