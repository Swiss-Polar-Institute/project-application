# Generated by Django 3.2.16 on 2022-11-04 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0179_trace_tracecoordinates'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tracecoordinates',
            old_name='latitude',
            new_name='lat',
        ),
        migrations.RenameField(
            model_name='tracecoordinates',
            old_name='longitude',
            new_name='lng',
        ),
    ]
