from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, DetailView

from project_core.forms.funding_instrument import FundingInstrumentForm
from project_core.models import FundingInstrument

FUNDING_INSTRUMENT_FORM_NAME = 'funding_instrument_form'


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


class FundingInstrumentUpdateView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        assert 'pk' in kwargs

        funding_instrument = FundingInstrument.objects.get(pk=kwargs['pk'])
        context['form'] = FundingInstrumentForm(instance=funding_instrument, prefix=FUNDING_INSTRUMENT_FORM_NAME)

        context['action_url'] = reverse('funding-instrument-update', kwargs={'pk': kwargs['pk']})
        context['active_section'] = 'calls'
        context['active_subsection'] = 'funding-instruments-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return render(request, 'management/funding_instrument-form.tmpl', context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'pk' in kwargs:
            funding_instrument = FundingInstrument.objects.get(id=kwargs['pk'])
            funding_instrument_form = FundingInstrumentForm(request.POST, instance=funding_instrument,
                                                            prefix=FUNDING_INSTRUMENT_FORM_NAME)

        else:
            funding_instrument_form = FundingInstrumentForm(request.POST, prefix=FUNDING_INSTRUMENT_FORM_NAME)

        if funding_instrument_form.is_valid():
            funding_instrument = funding_instrument_form.save()

            messages.success(request, 'Funding instrument has been saved')
            return redirect(reverse('funding-instrument-detail', kwargs={'pk': funding_instrument.pk}))

        context = super().get_context_data(**kwargs)

        context['form'] = funding_instrument_form
        context['action_url'] = reverse('funding-instrument-update', kwargs={'pk': kwargs['pk']})

        context['active_section'] = 'calls'
        context['active_subsection'] = 'funding-instruments-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        messages.error(request, 'Funding Instrument not saved. Please correct the errors inthe form and try again')

        return render(request, 'management/funding_instrument-form.tmpl', context)



# class FundingInstrumentUpdateView(FundingInstrumentMixin, AddCrispySubmitButtonMixin, SuccessMessageMixin, UpdateView):
#     template_name = 'management/funding_instrument-form.tmpl'
#     model = FundingInstrument
#     success_message = 'Funding instrument updated'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         context['active_section'] = 'calls'
#         context['active_subsection'] = 'funding-instruments-list'
#         context['sidebar_template'] = 'management/_sidebar-calls.tmpl'
#
#         return context


class FundingInstrumentDetailView(FundingInstrumentMixin, DetailView):
    template_name = 'management/funding_instrument-detail.tmpl'
    model = FundingInstrument

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_section'] = 'calls'
        context['active_subsection'] = 'funding-instruments-list'
        context['sidebar_template'] = 'management/_sidebar-calls.tmpl'

        return context
