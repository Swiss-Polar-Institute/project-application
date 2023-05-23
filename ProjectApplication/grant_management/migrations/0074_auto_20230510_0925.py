# Generated by Django 3.2.18 on 2023-05-10 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0073_medium_uploaded'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectsocialnetwork',
            name='published_date',
            field=models.DateField(blank=True, help_text='Date on which the outreach was published', null=True),
        ),
        migrations.AddField(
            model_name='projectsocialnetwork',
            name='title',
            field=models.CharField(blank=True, help_text='Title of outreach', max_length=1000, null=True),
        ),
    ]