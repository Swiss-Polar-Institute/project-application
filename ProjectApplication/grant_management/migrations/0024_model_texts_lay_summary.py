# Generated by Django 3.0.5 on 2020-05-01 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0118_calls_need_to_be_part_of_a_funding_instrument'),
        ('grant_management', '0023_renames_sent_date_to_payment_or_approval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='due_date',
            field=models.DateField(help_text='Date the document is due'),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='text',
            field=models.TextField(help_text='Blog post text'),
        ),
        migrations.AlterField(
            model_name='financialreport',
            name='approved_by',
            field=models.ForeignKey(blank=True, help_text='Person who approved the report', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.PhysicalPerson'),
        ),
        migrations.AlterField(
            model_name='financialreport',
            name='due_date',
            field=models.DateField(help_text='Date the document is due'),
        ),
        migrations.AlterField(
            model_name='financialreport',
            name='sent_for_approval_date',
            field=models.DateField(blank=True, help_text='Date the report was sent for approval', null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(help_text='Date the document is due'),
        ),
        migrations.AlterField(
            model_name='laysummary',
            name='author',
            field=models.ForeignKey(blank=True, help_text='Person who wrote the lay summary', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.PhysicalPerson'),
        ),
        migrations.AlterField(
            model_name='laysummary',
            name='due_date',
            field=models.DateField(help_text='Date the document is due'),
        ),
        migrations.AlterField(
            model_name='laysummary',
            name='text',
            field=models.TextField(blank=True, help_text='Lay summary text', null=True),
        ),
        migrations.AlterField(
            model_name='license',
            name='name',
            field=models.CharField(help_text='License name', max_length=30),
        ),
        migrations.AlterField(
            model_name='license',
            name='public_text',
            field=models.CharField(blank=True, help_text='Explanatory text for this license. Include the logo and URL to license text.', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='media',
            name='due_date',
            field=models.DateField(help_text='Date the document is due'),
        ),
        migrations.AlterField(
            model_name='scientificreport',
            name='approved_by',
            field=models.ForeignKey(blank=True, help_text='Person who approved the report', null=True, on_delete=django.db.models.deletion.PROTECT, to='project_core.PhysicalPerson'),
        ),
        migrations.AlterField(
            model_name='scientificreport',
            name='due_date',
            field=models.DateField(help_text='Date the document is due'),
        ),
        migrations.AlterField(
            model_name='scientificreport',
            name='sent_for_approval_date',
            field=models.DateField(blank=True, help_text='Date the report was sent for approval', null=True),
        ),
    ]