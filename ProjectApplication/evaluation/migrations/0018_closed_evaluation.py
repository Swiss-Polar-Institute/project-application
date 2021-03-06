# Generated by Django 3.0.3 on 2020-03-16 12:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluation', '0017_renames_closed_to_closed_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='callevaluation',
            name='closed_user',
            field=models.ForeignKey(blank=True, help_text='User by which the Call Evaluation was closed', null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='callevaluation',
            name='closed_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
