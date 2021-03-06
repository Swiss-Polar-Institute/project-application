# Generated by Django 3.0.10 on 2020-10-23 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0004_add_type_of_missing_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundinginstrumentyearmissingdata',
            name='missing_data_type',
            field=models.CharField(blank=True, choices=[('CAREER_STAGE_PROPOSAL_APPLICANT', 'Career Stage Proposal Applicant'), ('CAREER_STAGE_FUNDED_PROJECT_PI', 'Career Stage Funded Project PI'), ('GENDER_PROPOSAL_APPLICANT', 'Gender Proposal Applicant'), ('GENDER_FUNDED_PROJECT_PI', 'Gender Funded Project PI')], max_length=32, null=True),
        ),
    ]
