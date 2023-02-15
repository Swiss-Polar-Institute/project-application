# Generated by Django 3.2.16 on 2023-02-06 06:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0180_auto_20221104_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='finance_year',
            field=models.IntegerField(help_text='Finance year of this call. It is used, for example, for the project key from this call', validators=[django.core.validators.MinValueValidator(2015, 'Finance year cannot be before SPI existed'), django.core.validators.MaxValueValidator(2025, 'Finance year cannot be more than two years after the current year')]),
        ),
        migrations.AlterField(
            model_name='historicalcall',
            name='finance_year',
            field=models.IntegerField(help_text='Finance year of this call. It is used, for example, for the project key from this call', validators=[django.core.validators.MinValueValidator(2015, 'Finance year cannot be before SPI existed'), django.core.validators.MaxValueValidator(2025, 'Finance year cannot be more than two years after the current year')]),
        ),
        migrations.AlterField(
            model_name='historicalproject',
            name='finance_year',
            field=models.IntegerField(help_text='Finance year of this project', validators=[django.core.validators.MinValueValidator(2015, 'Finance year cannot be before SPI existed'), django.core.validators.MaxValueValidator(2025, 'Finance year cannot be more than two years after the current year')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='finance_year',
            field=models.IntegerField(help_text='Finance year of this project', validators=[django.core.validators.MinValueValidator(2015, 'Finance year cannot be before SPI existed'), django.core.validators.MaxValueValidator(2025, 'Finance year cannot be more than two years after the current year')]),
        ),
    ]
