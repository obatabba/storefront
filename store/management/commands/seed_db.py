from django.core.management import BaseCommand
from django.db import connection
from pathlib import Path
import os


class Command(BaseCommand):
    help = "Populate the database with collections and products."

    def handle(self, *args, **options):
        SEED_FILE = 'seed.sql'

        print('Populating the database...')
        current_dir = os.path.dirname(__file__)
        seed_file_path = os.path.join(current_dir, SEED_FILE)
        sql = Path(seed_file_path).read_text()

        with connection.cursor() as cursor:
            cursor.execute(sql)
        print('Done.')