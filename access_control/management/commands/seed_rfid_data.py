# management/commands/seed_rfid_data.py
from django.core.management.base import BaseCommand
from access_control.models import RFIDBadge
import random


class Command(BaseCommand):
    help = 'Seed the database with test RFID badges'

    def handle(self, *args, **options):
        uids = [
            "A1B2C3D4", "B2C3D4E5", "C3D4E5F6",
            "D4E5F6G7", "E5F6G7H8", "F6G7H8I9"
        ]

        for uid in uids:
            RFIDBadge.objects.get_or_create(
                uid=uid,
                defaults={'is_active': random.choice([True, False])}
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(uids)} RFID badges'))