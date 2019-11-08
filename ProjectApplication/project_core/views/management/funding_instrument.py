from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView

from project_core.models import FundingInstrument


class FundingInstrumentList(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context['funding_instruments'] = FundingInstrument.objects.all()

        context['active_section'] = 'calls'
        context['active_subsection'] = 'funding-instruments-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return render(request, 'management/funding_instrument-list.tmpl', context)


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


class FundingInstrumentCreateView(FundingInstrumentMixin, AddCrispySubmitButtonMixin, SuccessMessageMixin, CreateView):
    template_name = 'management/funding_instrument-form.tmpl'
    model = FundingInstrument
    success_message = 'Funding instrument created'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'calls'
        context['active_subsection'] = 'funding-instrument-add'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context


class FundingInstrumentUpdateView(FundingInstrumentMixin, AddCrispySubmitButtonMixin, SuccessMessageMixin, UpdateView):
    template_name = 'management/funding_instrument-form.tmpl'
    model = FundingInstrument
    success_message = 'Funding instrument updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'calls'
        context['active_subsection'] = 'funding-instruments-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context


class FundingInstrumentDetailView(FundingInstrumentMixin, DetailView):
    template_name = 'management/funding_instrument-detail.tmpl'
    model = FundingInstrument

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'calls'
        context['active_subsection'] = 'funding-instruments-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context
