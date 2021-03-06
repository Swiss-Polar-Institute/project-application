# Generated by Django 2.2.6 on 2020-01-08 10:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0098_required_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='draft_saved_mail_sent',
            field=models.BooleanField(default=False, help_text='True if the email informing the applicant that the draft has been saved has already been sent (usually is sent only once)'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='submitted_mail_sent',
            field=models.BooleanField(default=False, help_text='True if the email informing the applicant that the proposal has been submitted has been sent'),
        ),
        migrations.AlterField(
            model_name='callquestion',
            name='answer_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='physicalperson',
            name='phd_date',
            field=models.CharField(blank=True, help_text='Date (yyyy-mm) on which PhD awarded or expected', max_length=20, null=True, validators=[django.core.validators.RegexValidator(code='Invalid format', message='Format is yyyy-mm', regex='^[0-9]{4}-[0-9]{2}$')]),
        ),
        migrations.AlterField(
            model_name='templatequestion',
            name='answer_required',
            field=models.BooleanField(default=True),
        ),
    ]
