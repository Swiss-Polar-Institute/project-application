# Generated by Django 3.0.10 on 2020-10-23 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0002_add_reason_missing_data_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundinginstrumentyearmissingdata',
            name='description',
            field=models.CharField(help_text='Reason that there is missing data. It might be shown in the management', max_length=128),
        ),
    ]