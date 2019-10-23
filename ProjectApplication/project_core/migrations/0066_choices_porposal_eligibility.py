# Generated by Django 2.2.6 on 2019-10-23 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0065_createmodify_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='eligibility',
            field=models.CharField(choices=[('Eligibility not checked', 'Eligibility not checked'), ('Eligible', 'Eligible'), ('Not eligible', 'Not eligible')], default='Eligibility not checked', help_text='Status of eligibility of proposal', max_length=30),
        ),
    ]
