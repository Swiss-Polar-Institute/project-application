# Generated by Django 3.0.5 on 2020-05-12 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0031_improves_medium'),
    ]

    operations = [
        migrations.AddField(
            model_name='medium',
            name='blog_post',
            field=models.ManyToManyField(help_text='Which blog posts this image belongs to', to='grant_management.BlogPost'),
        ),
    ]
