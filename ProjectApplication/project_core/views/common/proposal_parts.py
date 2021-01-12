from project_core.forms.questions import Questions


class ProposalParts:
    def __init__(self, post, files, proposal, call=None):
        self._forms = []
        self._parts = []

        if proposal:
            call = proposal.call
        elif call:
            pass
        else:
            # It needs either the proposal or the call to find the questions
            assert False, 'In order to find the questions: pass either the Proposal or the Call'

        for part in call.parts():
            part.questions_form = Questions(post, files,
                                            proposal=proposal,
                                            call=call,
                                            call_part=part,
                                            prefix=ProposalParts._form_prefix(part))
            self._parts.append(part)

    def get_forms(self):
        forms = []

        for part in self._parts:
            forms.append(part.questions_form)

        return forms

    def get_parts(self):
        return self._parts

    @staticmethod
    def _form_prefix(part):
        from project_core.views.common.proposal import QUESTIONS_FORM_NAME

        return f'{QUESTIONS_FORM_NAME}-part-{part.pk}'
