# Generated by Django 3.2.3 on 2021-05-24 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0165_callcareerstage_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='long_name_english',
            field=models.CharField(blank=True, help_text='English name by which the organisation is known', max_length=100, null=True),
        ),
    ]
