# Generated by Django 3.0.5 on 2020-04-17 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0013_grant_management_help_texts'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financialreport',
            old_name='signed_by',
            new_name='approved_by',
        ),
    ]
