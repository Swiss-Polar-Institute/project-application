# Generated by Django 2.2.6 on 2020-02-07 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0100_funding_instrument_long_name_makes_unique'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='proposalcomment',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='proposalcomment',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='proposalcomment',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='proposalcomment',
            name='proposal',
        ),
        migrations.DeleteModel(
            name='CallComment',
        ),
        migrations.DeleteModel(
            name='ProposalComment',
        ),
    ]
