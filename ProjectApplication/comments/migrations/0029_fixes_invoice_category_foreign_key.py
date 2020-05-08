# Generated by Django 3.0.5 on 2020-05-06 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0028_invoicecomment_invoicecommentcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicecomment',
            name='category',
            field=models.ForeignKey(help_text='Type of comment', on_delete=django.db.models.deletion.PROTECT, to='comments.InvoiceCommentCategory'),
        ),
    ]