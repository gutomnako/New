# Generated by Django 5.1.4 on 2025-01-05 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_loginhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginhistory',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
