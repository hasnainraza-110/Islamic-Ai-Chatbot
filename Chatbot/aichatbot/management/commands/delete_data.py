from django.core.management.base import BaseCommand
from aichatbot.models import Topic, Question, Answer, Reference

class Command(BaseCommand):
    help = 'Delete all Q&A related data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting all entries...")

        Reference.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Topic.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All entries deleted successfully."))
