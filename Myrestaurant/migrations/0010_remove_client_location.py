# Generated by Django 5.2 on 2025-06-06 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Myrestaurant', '0009_alter_client_contact_alter_client_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='location',
        ),
    ]
