# Generated by Django 3.0.5 on 2020-05-20 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0122_funding_instrument_column_for_foreign_key_to_financial_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fundinginstrument',
            name='short_name_temp',
        ),
        migrations.RemoveField(
            model_name='historicalfundinginstrument',
            name='short_name_temp',
        ),
    ]
