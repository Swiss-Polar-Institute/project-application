# Generated by Django 2.2.6 on 2020-02-10 11:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0004_adds_attachments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalattachment',
            name='proposal',
            field=models.ForeignKey(help_text='Proposal that this attachments belongs to', on_delete=django.db.models.deletion.PROTECT, to='project_core.Proposal'),
        ),
        migrations.AlterField(
            model_name='proposalcommentcategory',
            name='comment_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='comments.Category'),
        ),
    ]
