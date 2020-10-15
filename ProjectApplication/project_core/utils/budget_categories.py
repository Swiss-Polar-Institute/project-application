from django.core.exceptions import ObjectDoesNotExist

from project_core.models import BudgetCategoryCall, BudgetCategory


def add_missing_budget_categories_call(call):
    # TODO: refactor and put it in add_missing_criterion_call_evaluation
    all_budget_category_ids = BudgetCategory.objects.all().values_list('id', flat=True)
    call_budget_category_ids = BudgetCategoryCall.objects.filter(call=call).values_list('budget_category__id',
                                                                                        flat=True)

    missing_ids = set(all_budget_category_ids) - set(call_budget_category_ids)

    for missing_id in missing_ids:
        try:
            budget_category = BudgetCategory.objects.get(id=missing_id)
        except ObjectDoesNotExist:
            # This category has been deleted between the time that the form was presented to now
            continue

        BudgetCategoryCall.objects.create(call=call, budget_category_id=missing_id, enabled=False,
                                          order=budget_category.order)
