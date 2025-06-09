from django.core.management.base import BaseCommand
from aichatbot.models import Hadith
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate hadith entries from the database'

    def handle(self, *args, **kwargs):
        duplicates = Hadith.objects.values('text').annotate(text_count=Count('text')).filter(text_count__gt=1)

        for duplicate in duplicates:
            text = duplicate['text']
            duplicate_entries = Hadith.objects.filter(text=text)
            
            # Keep the first entry and delete the rest
            first_entry = duplicate_entries.first()
            duplicate_entries.exclude(id=first_entry.id).delete()
            
            self.stdout.write(self.style.SUCCESS(f"Removed duplicate entries for text: {text}"))
