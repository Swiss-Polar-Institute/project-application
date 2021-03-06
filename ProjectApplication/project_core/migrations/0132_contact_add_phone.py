# Generated by Django 3.0.8 on 2020-08-03 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_core', '0131_add_postal_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callquestion',
            name='order',
            field=models.PositiveIntegerField(help_text='Use this number to order the questions'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='method',
            field=models.CharField(choices=[('Office', 'Office'), ('Mobile', 'Mobile'), ('Email', 'Email'), ('Phone', 'Phone')], help_text='Type of contact method', max_length=30),
        ),
        migrations.AlterField(
            model_name='historicalcallquestion',
            name='order',
            field=models.PositiveIntegerField(help_text='Use this number to order the questions'),
        ),
        migrations.AlterField(
            model_name='historicalcontact',
            name='method',
            field=models.CharField(choices=[('Office', 'Office'), ('Mobile', 'Mobile'), ('Email', 'Email'), ('Phone', 'Phone')], help_text='Type of contact method', max_length=30),
        ),
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together={('person_position', 'entry', 'method')},
        ),
    ]
