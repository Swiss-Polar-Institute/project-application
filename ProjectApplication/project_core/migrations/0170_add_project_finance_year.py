# Generated by Django 3.2.3 on 2021-11-11 16:06

from django.db import migrations, models

def copy_finance_year_from_calls_to_projects(apps, schema_editor):
    Project = apps.get_model('project_core', 'Project')

    for project in Project.objects.all():
        project.finance_year = project.call.finance_year
        project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0169_make_project_funding_instrument_not_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproject',
            name='finance_year',
            field=models.IntegerField(blank=True, help_text='Finance year of this project', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='finance_year',
            field=models.IntegerField(blank=True, help_text='Finance year of this project', null=True),
        ),

        migrations.RunPython(
            copy_finance_year_from_calls_to_projects
        )
    ]
