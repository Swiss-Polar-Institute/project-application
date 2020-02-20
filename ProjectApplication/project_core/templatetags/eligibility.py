from django import template

from project_core.models import Proposal

register = template.Library()


@register.filter(name='is_eligibility_not_set')
def is_eligibility_not_set(eligibility):
    return eligibility == Proposal.ELIGIBILITYNOTCHECKED


@register.filter(name='is_eligibility_eligible')
def is_eligibility_not_set(eligibility):
    return eligibility == Proposal.ELIGIBLE
