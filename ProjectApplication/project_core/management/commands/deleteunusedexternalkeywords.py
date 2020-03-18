from django.core.management import BaseCommand

from ...models import Keyword


class Command(BaseCommand):

    def handle(self, *args, **options):

        delete_keyword()


def delete_keyword():
    """Check if a keyword, created by an external user, has been used in a proposal or project. If it is not used, then delete it from the database."""

    # get keywords created by an external user
    keywords_external = Keyword.objects.filter(uid__source__source='External User')

    # get external keywords not used by a project or proposal.
    keywords_external_unused = keywords_external.filter(proposal__id=None).filter(project__id=None).delete()

