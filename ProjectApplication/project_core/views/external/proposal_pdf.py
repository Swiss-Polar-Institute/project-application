import os.path

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from ProjectApplication import settings
from project_core.views.common.proposal import AbstractProposalDetailView


def link_callback(uri, relative):
    if uri.startswith('http://') or uri.startswith('https://'):
        return uri
    elif uri.startswith(settings.STATIC_URL):
        resolved = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
        return resolved
    else:
        assert False, f'Unknown URI: {uri}'


class ProposalDetailViewPdf(AbstractProposalDetailView):
    template = 'external/proposal-detail.tmpl'

    def get(self, request, *args, **kwargs):
        context = self.prepare_context(request, *args, **kwargs)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="test.pdf"'

        # request is added in other usages of AbstractProposalDetailView.prepare_context context
        context['request'] = request
        template_path = get_template(self.template)
        html = template_path.render(context)

        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response
