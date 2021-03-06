# Generated by Django 2.2.6 on 2019-10-22 15:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_core', '0051_createmodify_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='source',
        ),
        migrations.CreateModel(
            name='CountryUid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('uid', models.CharField(help_text='Unique identifier', max_length=150, null=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='User by which the entry was created', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='project_core_countryuid_created_by_related', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, help_text='User by which the entry was modified', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='project_core_countryuid_modified_by_related', to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(help_text='Source of the UID', on_delete=django.db.models.deletion.PROTECT, to='project_core.Source')),
            ],
            options={
                'abstract': False,
                'unique_together': {('uid', 'source')},
            },
        ),
        migrations.AddField(
            model_name='country',
            name='uid',
            field=models.ForeignKey(default=None, help_text='Source of country name', on_delete=django.db.models.deletion.PROTECT, to='project_core.CountryUid'),
            preserve_default=False,
        ),
    ]
