from django.core.management.base import BaseCommand
from aichatbot.models import Ayaat, Book

class Command(BaseCommand):
    help = 'Import Hadith from a text file into the database and associate them with a book'

    def handle(self, *args, **kwargs):
        file_path = 'cleaned_extracted_quran_versesمعاملات.txt'
        book_title = 'معاملات'  # You can customize this title

        try:
            # Get or create the book by title
            book, created = Book.objects.get_or_create(title=book_title)

            with open(file_path, 'r', encoding='utf-8') as file:
                hadith_data = file.read().strip()

            # Assuming each hadith is separated by two line breaks
            hadith_list = hadith_data.split('\n\n')

            for hadith in hadith_list:
                if hadith.strip():  # Avoid inserting empty strings
                    Ayaat.objects.create(text=hadith.strip(), book=book)

            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported {len(hadith_list)} hadiths into book: {book_title}'
            ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error occurred: {e}'))
