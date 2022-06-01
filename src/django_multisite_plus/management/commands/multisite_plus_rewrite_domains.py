from django.core.management.base import BaseCommand, CommandError

from multisite.models import Alias

from django_multisite_plus.models import Site


class Command(BaseCommand):
    help = "Rewrites django.contrib.sites.Site based on settings.py"

    def handle(self, *args, **options):
        self.stdout.write(
            "Rewriting django.contrib.sites.Site based on local settings"
        )
        Site.objects.update_sites()

        self.stdout.write("Syncing multisite.Alias based on Sites")
        Alias.canonical.sync_all()

        self.stdout.write(self.style.SUCCESS("Done."))
