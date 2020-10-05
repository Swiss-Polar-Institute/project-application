from django.db import migrations, models, connection


def create_budget_category_calls(apps, schema_editor):
    BudgetCategoryCall = apps.get_model('project_core', 'BudgetCategoryCall')
    Call = apps.get_model('project_core', 'Call')

    for call in Call.objects.all():
        order_number = 1

        with connection.cursor() as cursor:
            # Raw SQL needed: The models in models.py might not have the fields (as they are removed at a later point)
            cursor.execute('''SELECT budgetcategory_id, name, project_core_budgetcategory.order FROM 
                    project_core_call_budget_categories 
                    LEFT JOIN project_core_budgetcategory 
                        ON project_core_call_budget_categories.budgetcategory_id=project_core_budgetcategory.id 
                    WHERE call_id=%s ORDER BY project_core_budgetcategory.order ASC, name ASC''', [call.id])
            for row in cursor.fetchall():
                budget_category_id = row[0]
                BudgetCategoryCall.objects.create(call=call, budget_category_id=budget_category_id, order=order_number)
                order_number += 1

def enable_all_budget_categories(apps, schema_editor):
    BudgetCategoryCall = apps.get_model('project_core', 'BudgetCategoryCall')

    BudgetCategoryCall.objects.all().update(enabled=True)


class Migration(migrations.Migration):
    dependencies = [
        ('project_core', '0139_budgetcategorycall_sortable'),
    ]

    operations = [
        migrations.RunPython(create_budget_category_calls),

        migrations.RemoveField(
            model_name='call',
            name='budget_categories',
        ),
        migrations.AddField(
            model_name='budgetcategorycall',
            name='enabled',
            field=models.BooleanField(default=False, help_text='Appears in the proposal form'),
        ),

        migrations.RunPython(enable_all_budget_categories),
    ]
