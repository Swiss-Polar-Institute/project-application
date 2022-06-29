# Generated by Django 3.2.13 on 2022-06-29 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0177_add_on_webite_field'),
        ('grant_management', '0064_coinvestors'),
    ]

    operations = [
        migrations.AddField(
            model_name='coinvestors',
            name='project',
            field=models.ForeignKey(default=1, help_text='Project to which the publication is related', on_delete=django.db.models.deletion.PROTECT, to='project_core.project'),
            preserve_default=False,
        ),
    ]
