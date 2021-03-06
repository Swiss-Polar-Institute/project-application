# Generated by Django 2.2.6 on 2019-12-05 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0097_physicalperson_phd_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='callquestion',
            name='answer_required',
            field=models.BooleanField(default=True, help_text='True if the answer is required'),
        ),
        migrations.AddField(
            model_name='templatequestion',
            name='answer_required',
            field=models.BooleanField(default=True, help_text='True if the answer is required'),
        ),
    ]
