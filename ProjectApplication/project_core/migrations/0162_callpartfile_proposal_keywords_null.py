# Generated by Django 3.1.5 on 2021-01-14 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0161_call_file_name_is_a_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callpartfile',
            name='description',
            field=models.CharField(blank=True, help_text='Description of this file', max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='keywords',
            field=models.ManyToManyField(blank=True, help_text='Keywords that describe the proposal', to='project_core.Keyword'),
        ),
    ]
