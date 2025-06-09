from django.db.models import Q
from .models import Topic, Question, Answer, Hadith, Reference

class ChatbotOntology:
    def __init__(self):
        pass

    def query_database(self, question):
        """
        Query the database to fetch relevant topics, questions, answers,
        hadiths, and references based on the input question.
        """
        # Find matching topics by name
        topics = Topic.objects.filter(name__icontains=question)

        # Prepare results
        results = []
        for topic in topics:
            topic_data = {
                "topic": topic.name,
                "questions": [question.text for question in topic.questions.all()],  # Updated to 'questions'
                "answers": [answer.text for answer in topic.answers.all()],  # Updated to 'answers'
                "hadiths": [hadith.text for hadith in topic.hadiths.all()],  # Updated to 'hadiths'
                "references": [reference.text for reference in topic.references.all()],  # 'references' remains the same
            }
            results.append(topic_data)

        if not results:
            return {"message": "No matching topics found."}

        return results
