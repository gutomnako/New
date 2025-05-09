# Generated by Django 5.1.4 on 2025-04-26 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0061_alter_resort_activity_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resort',
            name='cottage_price_range',
            field=models.CharField(choices=[('Low', 'Low'), ('Average', 'Average'), ('High', 'High')], default='Low', max_length=10),
        ),
        migrations.AddField(
            model_name='resort',
            name='room_price_range',
            field=models.CharField(choices=[('Low', 'Low'), ('Average', 'Average'), ('High', 'High')], default='Low', max_length=10),
        ),
    ]
