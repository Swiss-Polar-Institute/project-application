# Generated by Django 3.0.5 on 2020-05-12 13:20

from django.db import migrations, models

def add_basic_licenses(apps, schema_editor):
    License = apps.get_model('grant_management', 'License')

    License.objects.get_or_create(name='Creative Commons Attribution Share Alike 4.0 International',
                                  spdx_identifier='CC-BY-SA-4.0',
                                  public_text='<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.')

    License.objects.get_or_create(name='Creative Commons Attribution 4.0 International',
                                  spdx_identifier='CC-BY-4.0',
                                  public_text='<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.')


class Migration(migrations.Migration):

    dependencies = [
        ('grant_management', '0035_medium_makes_license_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='public_text',
            field=models.TextField(blank=True, help_text='Explanatory text for this license. Include the logo and URL to license text.', null=True),
        ),
        migrations.RunPython(add_basic_licenses),
    ]