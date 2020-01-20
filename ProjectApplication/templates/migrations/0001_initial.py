# Generated by Django 2.2.6 on 2020-01-20 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project_core', '0099_proposal_mails_sent'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateVariableName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('name', models.CharField(help_text='{{ name }} in the text where this gets replaced', max_length=200)),
                ('description', models.CharField(help_text='Definition of a variable', max_length=200)),
                ('created_by', models.ForeignKey(blank=True, help_text='User by which the entry was created', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='templates_templatevariablename_created_by_related', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, help_text='User by which the entry was modified', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='templates_templatevariablename_modified_by_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FundingInstrumentVariableTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('value', models.CharField(help_text='Value for the variable in this funding instrument', max_length=200)),
                ('created_by', models.ForeignKey(blank=True, help_text='User by which the entry was created', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='templates_fundinginstrumentvariabletemplate_created_by_related', to=settings.AUTH_USER_MODEL)),
                ('funding_instrument', models.ForeignKey(help_text='Funding instrument that this text belongs to', on_delete=django.db.models.deletion.PROTECT, to='project_core.FundingInstrument')),
                ('modified_by', models.ForeignKey(blank=True, help_text='User by which the entry was modified', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='templates_fundinginstrumentvariabletemplate_modified_by_related', to=settings.AUTH_USER_MODEL)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='templates.TemplateVariableName')),
            ],
            options={
                'unique_together': {('funding_instrument', 'name')},
            },
        ),
        migrations.CreateModel(
            name='CallVariableTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('value', models.CharField(help_text='Value for the variable in this funding instrument', max_length=200)),
                ('call', models.ForeignKey(help_text='Call that this text belongs to', on_delete=django.db.models.deletion.PROTECT, to='project_core.Call')),
                ('created_by', models.ForeignKey(blank=True, help_text='User by which the entry was created', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='templates_callvariabletemplate_created_by_related', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, help_text='User by which the entry was modified', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='templates_callvariabletemplate_modified_by_related', to=settings.AUTH_USER_MODEL)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='templates.TemplateVariableName')),
            ],
            options={
                'unique_together': {('call', 'name')},
            },
        ),
    ]