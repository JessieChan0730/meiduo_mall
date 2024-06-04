from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore


class Command(BaseCommand):
    help = "Runs Deletescheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.remove_all_jobs()
