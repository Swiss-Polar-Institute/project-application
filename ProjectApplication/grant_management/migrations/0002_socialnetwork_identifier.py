# Generated by Django 3.0.3 on 2020-04-06 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialnetwork',
            name='identifier',
            field=models.TextField(default='', help_text='Please enter social network login'),
        ),
    ]