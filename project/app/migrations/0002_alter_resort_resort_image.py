# Generated by Django 5.1.4 on 2024-12-31 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resort',
            name='resort_image',
            field=models.ImageField(default='paradise.jpg', help_text='Image of the resort', null=True, upload_to=''),
        ),
    ]
