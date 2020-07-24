# Generated by Django 3.0.7 on 2020-06-23 10:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0126_add_close_project_on_by_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalproject',
            name='allocated_budget',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Budget allocated to project', max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicalproject',
            name='status',
            field=models.CharField(choices=[('Ongoing', 'Ongoing'), ('Completed', 'Completed'), ('Aborted', 'Aborted')], default='Ongoing', help_text='Status of a project', max_length=30),
        ),
        migrations.AlterField(
            model_name='project',
            name='allocated_budget',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Budget allocated to project', max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('Ongoing', 'Ongoing'), ('Completed', 'Completed'), ('Aborted', 'Aborted')], default='Ongoing', help_text='Status of a project', max_length=30),
        ),
    ]