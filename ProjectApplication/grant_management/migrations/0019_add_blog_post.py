# Generated by Django 3.0.5 on 2020-04-29 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0118_calls_need_to_be_part_of_a_funding_instrument'),
        ('grant_management', '0018_remove_laysummary_sent_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laysummary',
            name='author',
            field=models.ForeignKey(blank=True, help_text='Person who wrote the Lay Summary', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.PhysicalPerson'),
        ),
        migrations.AlterField(
            model_name='laysummary',
            name='text',
            field=models.TextField(help_text='Lay Summary text'),
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('due_date', models.DateField(help_text='Date the document is expected to be received')),
                ('received_date', models.DateField(blank=True, help_text='Date the Blog post was received', null=True)),
                ('text', models.TextField(help_text='Blog post')),
                ('author', models.ForeignKey(blank=True, help_text='Person who wrote the blog post', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.PhysicalPerson')),
                ('project', models.ForeignKey(help_text='Abstract containing dates', on_delete=django.db.models.deletion.PROTECT, to='project_core.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]