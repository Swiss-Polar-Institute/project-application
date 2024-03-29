# Generated by Django 3.2.3 on 2021-10-25 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0167_organisation_display_name'),
        ('grant_management', '0058_alter_laysummary_verbose_name_plural'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('latitude', models.DecimalField(decimal_places=2, max_digits=6)),
                ('longitude', models.DecimalField(decimal_places=2, max_digits=7)),
                ('name', models.CharField(max_length=100)),
                ('project', models.ForeignKey(help_text='Project that the coordinate belongs to', on_delete=django.db.models.deletion.PROTECT, related_name='project_location', to='project_core.project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
