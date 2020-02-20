# Generated by Django 2.2.6 on 2020-02-10 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0005_fixes_onetoone_to_foreign_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalcommentcategory',
            name='comment_category',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='comments.Category'),
        ),
    ]