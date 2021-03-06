# Generated by Django 2.2.4 on 2019-09-25 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0007_rename_person_organisation_to_organisations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callquestion',
            name='answer_type',
            field=models.CharField(choices=[('Text', 'Text')], default='Text', help_text='Type of field that should be applied to the question answer', max_length=5),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='description',
            field=models.CharField(help_text='Description of a keyword that should be used to distinguish it from another keyword', max_length=512),
        ),
        migrations.AlterUniqueTogether(
            name='proposalqatext',
            unique_together={('proposal', 'call_question')},
        ),
        migrations.AlterUniqueTogether(
            name='proposedbudgetitem',
            unique_together={('category', 'proposal')},
        ),
    ]
