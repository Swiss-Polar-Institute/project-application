# Generated by Django 3.2.13 on 2022-06-28 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0177_add_on_webite_field'),
        ('grant_management', '0063_fieldnote'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoInvestors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('co_investor', models.ForeignKey(blank=True, help_text='Co Investor', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.physicalperson')),
                ('organisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.organisation')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
