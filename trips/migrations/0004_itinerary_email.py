# Generated by Django 5.1.7 on 2025-04-21 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0003_itinerary_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerary',
            name='email',
            field=models.CharField(default='Anonymous', max_length=150),
        ),
    ]
