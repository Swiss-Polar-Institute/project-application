# Generated by Django 3.2.3 on 2021-11-18 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0172_project_call_null_and_historical_finance_year_not_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialkey',
            name='funding_instrument',
            field=models.BooleanField(default=True, help_text='This financial key is booked or used for a funding instrument'),
        ),
    ]
