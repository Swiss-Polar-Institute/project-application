# Generated by Django 3.0.10 on 2020-10-12 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0056_rename_file_field_medium'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediumDeleted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('original_id', models.IntegerField(help_text='ID of the delete Medium.ID. Used to return them to the SPI Media Gallery or other software', unique=True)),
            ],
            options={
                'verbose_name_plural': 'MediaDeleted',
            },
        ),
    ]
