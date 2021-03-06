# Generated by Django 3.0.3 on 2020-04-14 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0010_makes_signed_by_optional'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialreport',
            name='sent_for_approval_date',
        ),
        migrations.AddField(
            model_name='financialreport',
            name='approval_date',
            field=models.DateField(blank=True, help_text='Date that the finance report was approved', null=True),
        ),
    ]
