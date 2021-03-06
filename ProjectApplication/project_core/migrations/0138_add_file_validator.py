# Generated by Django 3.0.10 on 2020-09-21 10:38

from django.db import migrations, models
import project_core.utils.utils
import storages.backends.s3boto3


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0137_delete_head_of_research_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalqafile',
            name='file',
            field=models.FileField(storage=storages.backends.s3boto3.S3Boto3Storage(), upload_to='proposals_qa/', validators=[*project_core.utils.utils.external_file_validator()]),
        ),
    ]
