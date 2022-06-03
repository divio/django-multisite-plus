from django.core.management.base import BaseCommand, CommandError

from django_multisite_plus.models import Site


class Command(BaseCommand):
    help = "Syncs django_multisite_plus sites based on settings.py"

    def handle(self, *args, **options):
        self.stdout.write(
            "Syncing django_multisite_plus Sites based on settings"
        )
        Site.objects.auto_populate_sites()

        self.stdout.write(self.style.SUCCESS("Done."))
