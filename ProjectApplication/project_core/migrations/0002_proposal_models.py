# Generated by Django 2.2.4 on 2019-09-20 09:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the budget category', max_length=100)),
                ('description', models.CharField(help_text='Description of the budget category', max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.CharField(help_text='Email address', max_length=100)),
                ('work_telephone', models.CharField(help_text='Work telephone number', max_length=20)),
                ('mobile', models.CharField(blank=True, help_text='Mobile telephone number', max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Country name', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='FundingStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(help_text='Name of the status', max_length=30)),
                ('description', models.CharField(help_text='Decsription of the status', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GeographicArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(help_text='Name of geograpic area', max_length=100)),
                ('definition', models.CharField(help_text='Detailed description of the geographic area to avoid duplicate entries or confusion', max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of a keyword', max_length=128)),
                ('description', models.CharField(help_text='Decsription of a keyword that should be used to distinguish it from another keyword', max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_type', models.CharField(choices=[('CI', 'Call introductory message')], help_text='Identification of where the message is to be used', max_length=5)),
                ('message', models.TextField(help_text='Text of the message')),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('long_name', models.CharField(help_text='Full name by which the organisation is known', max_length=100)),
                ('short_name', models.CharField(blank=True, help_text='Short name by which the organisation is commonly known', max_length=50, null=True)),
                ('address', models.CharField(blank=True, help_text='Address of the organisation', max_length=1000, null=True)),
                ('country', models.ForeignKey(help_text='Country in which the organisation is based', on_delete=django.db.models.deletion.PROTECT, to='project_core.Country')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='First name(s) of a person', max_length=100)),
                ('surname', models.CharField(help_text='Last name(s) of a person', max_length=100)),
                ('group', models.CharField(blank=True, help_text='Name of the working group, department, laboratory for which the person works', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PersonTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Personal or academic title used by a person', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the proposal being submitted', max_length=1000)),
                ('location', models.CharField(blank=True, help_text='More precise location of where proposal would take place (not coordinates)', max_length=200, null=True)),
                ('start_time_frame', models.CharField(help_text='Approximate date on which the proposed project is expected to start', max_length=100)),
                ('duration', models.CharField(help_text='Period of time expected that the proposed project will last', max_length=100)),
                ('summary', models.TextField(help_text='Summary of the proposal submitted for funding')),
                ('description', models.TextField(help_text='Outline of proposal')),
                ('requested_funds_explanation', models.TextField(help_text='Explanation about how proposed funds would be used')),
                ('logistics_requirements', models.TextField(help_text='Description of requirements regarding logistics and local partners')),
                ('applicant', models.ForeignKey(help_text='Main applicant of the proposal', on_delete=django.db.models.deletion.PROTECT, to='project_core.Person')),
                ('geographical_area', models.ForeignKey(help_text='Description of the geographical area covered by the proposal', on_delete=django.db.models.deletion.PROTECT, to='project_core.GeographicArea')),
                ('keywords', models.ManyToManyField(help_text='Keywords that describe the topic of the proposal', to='project_core.Keyword')),
            ],
        ),
        migrations.CreateModel(
            name='ProposalFundingItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Amount given in funding', max_digits=10)),
                ('organisation', models.ForeignKey(help_text='Name of organisation from which the funding is sourced', on_delete=django.db.models.deletion.PROTECT, to='project_core.Organisation')),
                ('proposal', models.ForeignKey(help_text='Proposal for which the funding has been sourced', on_delete=django.db.models.deletion.PROTECT, to='project_core.Proposal')),
                ('status', models.ForeignKey(help_text='Status of the funding item', on_delete=django.db.models.deletion.PROTECT, to='project_core.FundingStatus')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProposalStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the status of the proposal table', max_length=50)),
                ('description', models.CharField(help_text='Detailed description of the proposal status name', max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='ProposedBudgetItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('details', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2, help_text='Cost of category item', max_digits=10, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='project_core.BudgetCategory')),
                ('proposal', models.ForeignKey(help_text='Proposal it which the budget item relates', on_delete=django.db.models.deletion.PROTECT, to='project_core.Proposal')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of a step', max_length=60)),
                ('description', models.CharField(help_text='Description of a step', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='StepDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(help_text='Date and time of notable date', max_length=64)),
                ('step', models.ForeignKey(help_text='Name of step', max_length=128, on_delete=django.db.models.deletion.PROTECT, to='project_core.Step')),
            ],
        ),
        migrations.RemoveField(
            model_name='call',
            name='dates',
        ),
        migrations.AddField(
            model_name='call',
            name='budget_maximum',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Maximum amount that can be requested in the proposal budget', max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='call',
            name='call_open_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Date on which the call is opened'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='call',
            name='introductory_message',
            field=models.TextField(blank=True, help_text='Introductory text to the call for applicants', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='submission_deadline',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Submission deadline of the call'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='call',
            name='long_name',
            field=models.CharField(help_text='Full name of the call', max_length=200),
        ),
        migrations.AlterField(
            model_name='call',
            name='short_name',
            field=models.CharField(blank=True, help_text='Short name or acronym of the call', max_length=60, null=True),
        ),
        migrations.DeleteModel(
            name='Date',
        ),
        migrations.AddField(
            model_name='proposal',
            name='proposal_status',
            field=models.ForeignKey(help_text='Status or outcome of the proposal', on_delete=django.db.models.deletion.PROTECT, to='project_core.ProposalStatus'),
        ),
        migrations.AddField(
            model_name='person',
            name='academic_title',
            field=models.ForeignKey(help_text='Title of the person', on_delete=django.db.models.deletion.PROTECT, to='project_core.PersonTitle'),
        ),
        migrations.AddField(
            model_name='person',
            name='organisation',
            field=models.ManyToManyField(help_text='Organisation(s) represented by the person', to='project_core.Organisation'),
        ),
        migrations.AddField(
            model_name='contact',
            name='person',
            field=models.ForeignKey(help_text='Person to which the contact details belong', on_delete=django.db.models.deletion.PROTECT, to='project_core.Person'),
        ),
        migrations.AddField(
            model_name='call',
            name='budget_categories',
            field=models.ManyToManyField(help_text='Categories required for the budget for a call', to='project_core.BudgetCategory'),
        ),
    ]
