# Generated by Django 5.1.4 on 2025-03-28 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_alter_resort_hero_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resort',
            name='amenities',
            field=models.ManyToManyField(blank=True, help_text='Amenities available at the resort', related_name='resorts', to='app.amenity'),
        ),
    ]
