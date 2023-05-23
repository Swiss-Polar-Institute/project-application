# Generated by Django 3.2.16 on 2023-02-13 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0071_auto_20221107_1715'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, help_text='Date and time at which the entry was created')),
                ('modified_on', models.DateTimeField(auto_now=True, help_text='Date and time at which the entry was modified', null=True)),
                ('name', models.CharField(blank=True, help_text='Title of the blog post', max_length=1024, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='medium',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='Which tags this image belongs to', to='grant_management.Tag'),
        ),
    ]