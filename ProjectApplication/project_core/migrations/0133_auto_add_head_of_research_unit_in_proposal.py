# Generated by Django 3.0.8 on 2020-08-10 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0132_contact_add_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproposal',
            name='head_of_research_unit',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='Head of the research unit of this application', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='project_core.PersonPosition'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='head_of_research_unit',
            field=models.ForeignKey(help_text='Head of the research unit of this application', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='head_of_research_unit', to='project_core.PersonPosition'),
        ),
        migrations.AlterField(
            model_name='postaladdress',
            name='address',
            field=models.TextField(help_text='Include department name, street/avenue, block, building, floor, door, etc.'),
        ),
    ]
