# Generated by Django 3.0.5 on 2020-05-12 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0037_medium_renames_author_to_photographer'),
    ]

    operations = [
        migrations.AddField(
            model_name='medium',
            name='descriptive_text',
            field=models.TextField(blank=True, help_text='Description of this media, if provided. Where was it taken, context, etc.', null=True),
        ),
    ]
