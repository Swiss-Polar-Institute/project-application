# Generated by Django 3.2.19 on 2023-05-11 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0074_auto_20230510_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='reference',
            field=models.CharField(blank=True, help_text='Full reference of dataset', max_length=1000, null=True),
        ),
    ]
