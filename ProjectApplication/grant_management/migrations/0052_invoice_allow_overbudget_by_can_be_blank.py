# Generated by Django 3.0.7 on 2020-07-21 15:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grant_management', '0051_add_boolean_to_allow_invoice_go_overbudget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='overbudget_allowed_by',
            field=models.ForeignKey(blank=True, help_text='User that allowed the overbudget', null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]