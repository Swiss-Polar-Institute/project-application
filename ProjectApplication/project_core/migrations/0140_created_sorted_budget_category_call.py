# Generated by Django 3.0.10 on 2020-09-28 10:30

from django.db import migrations


def create_budget_category_calls(apps, schema_editor):
    BudgetCategoryCall = apps.get_model('project_core', 'BudgetCategoryCall')
    Call = apps.get_model('project_core', 'Call')

    for call in Call.objects.all():
        order_number = 1

        for budget_category in call.budget_categories.all().order_by('order', 'name'):
            BudgetCategoryCall.objects.create(call=call, budget_category=budget_category, order=order_number)
            order_number += 1


class Migration(migrations.Migration):
    dependencies = [
        ('project_core', '0139_budgetcategorycall_sortable'),
    ]

    operations = [
        migrations.RunPython(create_budget_category_calls)
    ]
