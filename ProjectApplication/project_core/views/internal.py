from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy
from ..models import Proposal
from django.shortcuts import render, redirect
from ..forms.call import CallForm
from ..models import Call

CALL_FORM_NAME = 'call_form'


class ProposalsList(TemplateView):
    template_name = 'internal/list_proposals.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['proposals'] = Proposal.objects.all()

        return context


class InternalHomepage(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        return render(request, 'internal/homepage.tmpl', context)


class InternalCallsList(TemplateView):
    template_name = 'internal/call-list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['calls'] = Call.objects.all()

        return context


class CallView(TemplateView):
    def get(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'id' in kwargs:
            call_id = kwargs['id']
            call = Call.objects.get(id=call_id)

            context[CALL_FORM_NAME] = CallForm(instance=call)
        else:
            context[CALL_FORM_NAME] = CallForm()

        return render(request, 'internal/call.tmpl', context)

    def post(self, request, *args, **kwargs):
        super().get_context_data(**kwargs)

        context = {}

        if 'id' in kwargs:
            call = Call.objects.get(id=kwargs['id'])
            call_form = CallForm(request.POST, instance=call)

            context['call_action_url'] = reverse('call-update', kwargs={'id': call.id})
            context['action'] = 'modified'

        else:
            # creates a call
            call_form = CallForm(request.POST)
            context['call_action_url'] = reverse('call-add')
            context['action'] = 'created'

        if call_form.is_valid():
            call = call_form.save()

            context['id'] = call.id

            return render(request, 'internal/call-modified.tmpl', context)

        context = {}

        context[CALL_FORM_NAME] = call_form

        return render(request, 'internal/call.tmpl', context)
