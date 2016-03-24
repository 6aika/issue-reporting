import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import MediaFile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Deleted unneeded temporary media files and MediaFile objects from MEDIA_ROOT"

    def add_arguments(self, parser):
        parser.add_argument("--force",
                            action="store_true",
                            help="Prevent asking for confirmation of deletion.")
        parser.add_argument("--silent",
                            action="store_true",
                            help="Don't display info about deletion and files.")

        parser.add_argument("--days",
                            type=int,
                            default=1,
                            required=False,
                            help="Script will delete files which are more than DAYS days old. Default is 1.")

    def handle(self, *args, **options):
        delete_date = timezone.now() - timedelta(days=options["days"])
        all_files = MediaFile.objects.all()
        old_files = MediaFile.objects.filter(date_created__lt=delete_date)
        if not options["silent"]:
            logger.info("Deleting", old_files.count(), "/", all_files.count(), "files created before",
                        delete_date.strftime("%A %d.%m.%y %H:%M"))
        if not old_files.count():
            if not options["silent"]:
                logger.info("Nothing to delete!")
            return

        if not options["force"]:
            answer = input("Enter 'yes' to confirm: ")
            if answer != "yes":
                logger.info("Aborting...")
                return
            else:
                logger.info("Deleting...")

        for file in old_files:
            if not options["silent"]:
                logger.info(file.file.name)
            file.file.delete()
            file.delete()
