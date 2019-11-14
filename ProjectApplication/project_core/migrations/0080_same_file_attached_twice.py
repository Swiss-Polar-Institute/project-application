# Generated by Django 2.2.6 on 2019-11-14 12:15

from django.db import migrations, models
import storages.backends.s3boto3


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0079_budget_helptext'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalqafile',
            name='file',
            field=models.FileField(storage=storages.backends.s3boto3.S3Boto3Storage(), upload_to='proposals_qa/'),
        ),
        migrations.AlterField(
            model_name='proposalqafile',
            name='md5',
            field=models.CharField(db_index=True, max_length=32),
        ),
    ]
