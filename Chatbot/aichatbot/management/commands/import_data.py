import os
import re
from django.core.management.base import BaseCommand
from aichatbot.models import Topic, Question, Answer, Reference, Book

class Command(BaseCommand):
    help = 'Import fatawa from a structured text file into Topic, Question, Answer, and Reference models with Book info'

    def handle(self, *args, **options):
        filepath = 'updated_معاملات.txt'  # 🔁 Change this to your actual path
        book_title = 'معاملات'  # ✅ Customize the book title here

        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f'❌ File not found: {filepath}'))
            return

        # Get or create the book instance
        book, _ = Book.objects.get_or_create(title=book_title)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = re.split(r'\n(?=عنوان:)', content.strip())
        count = 0

        for block in blocks:
            title_match = re.search(r'عنوان:\s*(.+)', block)
            question_match = re.search(r'سوال:\s*(.+)', block)
            answer_match = re.search(r'جواب:\s*(.+?)(?=\nReference:|\Z)', block, re.DOTALL)
            reference_matches = re.findall(r'Reference:\s*(.+)', block)

            if title_match and question_match and answer_match:
                title = title_match.group(1).strip()
                question = question_match.group(1).strip()
                answer = answer_match.group(1).strip()

                topic, _ = Topic.objects.get_or_create(name=title)

                # Create and link with the book
                Question.objects.create(topic=topic, text=question, book=book)
                Answer.objects.create(topic=topic, text=answer, book=book)

                for ref in reference_matches:
                    Reference.objects.create(topic=topic, text=ref.strip(), book=book)

                count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Imported topic: {title}'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Skipped a block due to missing fields.'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Total topics imported: {count} into book: {book_title}'))
