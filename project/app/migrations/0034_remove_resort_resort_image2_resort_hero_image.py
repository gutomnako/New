# Generated by Django 5.1.4 on 2025-03-17 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_alter_resort_amenities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resort',
            name='resort_image2',
        ),
        migrations.AddField(
            model_name='resort',
            name='hero_image',
            field=models.ImageField(blank=True, null=True, upload_to='resort_images/'),
        ),
    ]
