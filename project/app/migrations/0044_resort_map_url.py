# Generated by Django 5.1.4 on 2025-04-09 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_alter_resort_activities_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='resort',
            name='map_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
