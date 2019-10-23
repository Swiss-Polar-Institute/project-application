# Generated by Django 2.2.6 on 2019-10-23 06:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_core', '0060_createmodify_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='geographicalarea',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='User by which the entry was created', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='project_core_geographicalarea_created_by_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='geographicalarea',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=None, help_text='Date and time at which the entry was created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='geographicalarea',
            name='modified_by',
            field=models.ForeignKey(blank=True, help_text='User by which the entry was modified', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='project_core_geographicalarea_modified_by_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='geographicalarea',
            name='modified_on',
            field=models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True),
        ),
    ]
