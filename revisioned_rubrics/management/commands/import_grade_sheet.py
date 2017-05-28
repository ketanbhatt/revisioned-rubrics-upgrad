from __future__ import absolute_import

from django.core.management import BaseCommand

from revisioned_rubrics.models import Attempt


class Command(BaseCommand):
    help = "Import Grading Sheet"

    def add_arguments(self, parser):
        parser.add_argument('grading_sheet', type=str, help="Name of the Grading sheet CSV")
        parser.add_argument('--attempt', type=int, help="ID of the Attempt")
        parser.add_argument('--revision', type=int, help="ID of the Revision")

    def handle(self, *args, **options):
        self.stdout.write("############### Importing Grading sheet ####################")

        Attempt.import_grade_sheet(
            options['grading_sheet'], options['attempt'], options['revision']
        )

        self.stdout.write("############### Grading sheet imported ####################")
