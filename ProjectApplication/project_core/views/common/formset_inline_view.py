from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class InlineFormsetUpdateView(TemplateView):
    inline_formset = None
    human_type = None
    human_type_plural = None
    parent = None
    extra_content = None
    url_id = 'pk'
    template_name = 'grant_management/formset.tmpl'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.human_type_plural is None:
            self.human_type_plural = f'{self.human_type}s'

    def get_extra_context(self):
        context = {}

        context['title'] = self.human_type_plural.capitalize()

        context['human_type'] = self.human_type

        context['save_text'] = f'Save {self.human_type_plural.title()}'

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context.update(self.get_extra_context())

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context.update(self.get_extra_context())

        form_kwargs = {}

        if hasattr(self.inline_formset, 'wants_user') and self.inline_formset.wants_user:
            form_kwargs = {'user': request.user}

        if hasattr(self.inline_formset, 'can_force_save') and self.inline_formset.can_force_save:
            form_kwargs = {'save_force': 'save_force' in request.POST}

        forms = self.inline_formset(request.POST, request.FILES, prefix='FORM_SET',
                                    instance=context['project'],
                                    form_kwargs=form_kwargs)

        if forms.is_valid():
            forms.save()
            messages.success(request, f'{self.human_type_plural.capitalize()} saved')
            return redirect(context['destination_url'])

        messages.error(request, f'{self.human_type_plural.capitalize()} not saved. Verify errors in the form')

        if hasattr(forms, 'force_save_text'):
            context['force_save_text'] = forms.force_save_text()

        context['FORM_SET'] = forms

        return render(request, self.template_name, context)
