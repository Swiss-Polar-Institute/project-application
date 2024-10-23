# Generated by Django 3.2.23 on 2024-06-21 06:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0187_auto_20240621_0733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personposition',
            name='academic_title',
            field=models.ForeignKey(blank=True, help_text='Title of the person', null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_core.persontitle'),
        ),
    ]