# Generated by Django 5.1.4 on 2025-03-31 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_alter_resort_amenities'),
    ]

    operations = [
        migrations.AddField(
            model_name='resort',
            name='activities_image',
            field=models.ImageField(blank=True, null=True, upload_to='resorts/activity/'),
        ),
        migrations.AddField(
            model_name='resort',
            name='activity_description',
            field=models.TextField(blank=True, help_text='Brief description of the resort', null=True),
        ),
        migrations.AddField(
            model_name='resort',
            name='beach_description',
            field=models.TextField(blank=True, help_text='Brief description of the resort', null=True),
        ),
        migrations.AddField(
            model_name='resort',
            name='beachimage',
            field=models.ImageField(blank=True, null=True, upload_to='resorts/beach/'),
        ),
        migrations.AddField(
            model_name='resort',
            name='room_description',
            field=models.TextField(blank=True, help_text='Brief description of the resort', null=True),
        ),
        migrations.AddField(
            model_name='resort',
            name='roomimage',
            field=models.ImageField(blank=True, null=True, upload_to='resorts/rooms/'),
        ),
    ]
