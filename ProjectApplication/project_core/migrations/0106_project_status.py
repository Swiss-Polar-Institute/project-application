# Generated by Django 3.0.3 on 2020-02-19 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0105_project_projectpartner'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='ONGOING', help_text='Status of a project', max_length=30),
        ),
    ]