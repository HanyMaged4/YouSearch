from django.core.management.base import BaseCommand
import json
from pathlib import Path


class Command(BaseCommand):

    def handle(self, *args, **options):
        urls_path = Path(__file__).resolve().parents[2] / 'data' / 'urls.json'

        if not urls_path.exists():
            self.stderr.write(f"URLs file not found: {urls_path}")
            return

        with urls_path.open('r', encoding='utf-8') as file:
            url_list = json.load(file)

        for url in url_list:
            print(f"Processing: {url}")