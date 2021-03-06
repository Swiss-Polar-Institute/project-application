# Generated by Django 2.2.6 on 2019-10-23 06:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0063_geographicalarea_uid_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='uid',
            field=models.ForeignKey(blank=True, help_text='UID of country name', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.CountryUid'),
        ),
        migrations.AlterField(
            model_name='geographicalarea',
            name='uid',
            field=models.ForeignKey(blank=True, help_text='UID of a geographical area', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.GeographicalAreaUid'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='uid',
            field=models.ForeignKey(help_text='UID of a country', on_delete=django.db.models.deletion.PROTECT, to='project_core.OrganisationUid'),
        ),
        migrations.AlterField(
            model_name='source',
            name='description',
            field=models.TextField(blank=True, help_text='Description of the source eg. URL, version', null=True),
        ),
    ]
