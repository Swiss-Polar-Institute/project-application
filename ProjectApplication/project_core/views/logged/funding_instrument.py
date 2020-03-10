from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView

from project_core.forms.funding_instrument import FundingInstrumentForm
from project_core.models import FundingInstrument
from variable_templates.forms.template_variables import TemplateVariableItemFormSet
from variable_templates.utils import get_template_variables_for_funding_instrument

FUNDING_INSTRUMENT_FORM_NAME = 'funding_instrument_form'
TEMPLATE_VARIABLES_FORM_NAME = 'template_variables_form'


class FundingInstrumentList(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['funding_instruments'] = FundingInstrument.objects.all()

        context.update({'active_section': 'calls',
                        'active_subsection': 'funding-instruments-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['breadcrumb'] = [{'name': 'Funding instruments'}]

        return render(request, 'logged/funding_instrument-list.tmpl', context)


class FundingInstrumentMixin:
    fields = ['long_name', 'short_name', 'description']

    @property
    def success_msg(self):
        return NotImplemented


class AddCrispySubmitButtonMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Submit'))

        return form


class FundingInstrumentView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'pk' in kwargs:
            funding_instrument = FundingInstrument.objects.get(pk=kwargs['pk'])
            context[FUNDING_INSTRUMENT_FORM_NAME] = FundingInstrumentForm(instance=funding_instrument,
                                                                          prefix=FUNDING_INSTRUMENT_FORM_NAME)
            context[TEMPLATE_VARIABLES_FORM_NAME] = TemplateVariableItemFormSet(funding_instrument=funding_instrument,
                                                                                prefix=TEMPLATE_VARIABLES_FORM_NAME)

            context['action_url'] = reverse('funding-instrument-update', kwargs={'pk': kwargs['pk']})

            context.update({'active_section': 'calls',
                            'active_subsection': 'funding-instruments-list',
                            'sidebar_template': 'logged/_sidebar-calls.tmpl'})

            breadcrumb = 'Edit'

        else:
            context[FUNDING_INSTRUMENT_FORM_NAME] = FundingInstrumentForm(prefix=FUNDING_INSTRUMENT_FORM_NAME)
            context[TEMPLATE_VARIABLES_FORM_NAME] = TemplateVariableItemFormSet(prefix=TEMPLATE_VARIABLES_FORM_NAME)

            context.update({'active_section': 'calls',
                            'active_subsection': 'funding-instrument-add',
                            'sidebar_template': 'logged/_sidebar-calls.tmpl'})

            breadcrumb = 'Create'

        context['breadcrumb'] = [{'name': 'Funding instruments'},
                                 {'name': breadcrumb}]

        return render(request, 'logged/funding_instrument-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'pk' in kwargs:
            funding_instrument = FundingInstrument.objects.get(id=kwargs['pk'])
            funding_instrument_form = FundingInstrumentForm(request.POST, instance=funding_instrument,
                                                            prefix=FUNDING_INSTRUMENT_FORM_NAME)



        else:
            funding_instrument_form = FundingInstrumentForm(request.POST, prefix=FUNDING_INSTRUMENT_FORM_NAME)

        template_variables_form = TemplateVariableItemFormSet(request.POST, prefix=TEMPLATE_VARIABLES_FORM_NAME)

        if funding_instrument_form.is_valid() and template_variables_form.is_valid():
            funding_instrument = funding_instrument_form.save()

            template_variables_form.save_into_funding_instrument(funding_instrument)

            messages.success(request, 'Funding instrument has been saved')
            return redirect(reverse('funding-instrument-detail', kwargs={'pk': funding_instrument.pk}))

        context[FUNDING_INSTRUMENT_FORM_NAME] = funding_instrument_form
        context[TEMPLATE_VARIABLES_FORM_NAME] = template_variables_form

        context['action_url'] = reverse('funding-instrument-update', kwargs={'pk': kwargs['pk']})

        context.update({'active_section': 'calls',
                        'active_subsection': 'funding-instruments-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        messages.error(request, 'Funding Instrument not saved. Please correct the errors in the form and try again')

        return render(request, 'logged/funding_instrument-form.tmpl', context)


# class FundingInstrumentUpdateView(FundingInstrumentMixin, AddCrispySubmitButtonMixin, SuccessMessageMixin, UpdateView):
#     template_name = 'logged/funding_instrument-form.tmpl'
#     model = FundingInstrument
#     success_message = 'Funding instrument updated'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         context['active_section'] = 'calls'
#         context['active_subsection'] = 'funding-instruments-list'
#         context['sidebar_template'] = 'logged/_sidebar-calls.tmpl'
#
#         return context


class FundingInstrumentDetailView(FundingInstrumentMixin, DetailView):
    template_name = 'logged/funding_instrument-detail.tmpl'
    model = FundingInstrument

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({'active_section': 'calls',
                        'active_subsection': 'funding-instruments-list',
                        'sidebar_template': 'logged/_sidebar-calls.tmpl'})

        context['template_variables'] = get_template_variables_for_funding_instrument(kwargs['object'])

        return context
