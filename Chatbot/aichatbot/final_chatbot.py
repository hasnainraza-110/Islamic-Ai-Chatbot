from owlready2 import get_ontology, Thing, DataProperty
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from LughaatNLP import LughaatNLP
from django.apps import apps
import re

# Class to Manage Query History
class History:
    def __init__(self):
        self.last_topic = None

    def update_last_topic(self, topic):
        self.last_topic = topic

    def get_last_topic(self):
        return self.last_topic

# Class to Process Urdu Text
class UrduTextProcessor:
    def __init__(self):
        self.text_processor = LughaatNLP()
        self.stopwords = set([
            "کے", "کی", "کہ", "یہ", "اور", "ہے", "کو", "میں", "سے",
            "پر", "تو", "کا", "بھی", "کر", "گے", "کرنا", "تھا", "ہوں"
        ])

    def preprocess_text(self, text):
        normalized_text = self.text_processor.normalize(text)
        cleaned_text = re.sub(r'[^\w\s]', '', normalized_text)
        tokens = self.text_processor.urdu_tokenize(cleaned_text)
        filtered_text = " ".join([token for token in tokens if token not in self.stopwords])
        return self.text_processor.lemmatize_sentence(filtered_text)

    def preprocess_text_with_focus(self, text):
        normalized_text = self.text_processor.normalize(text)
        cleaned_text = re.sub(r'[^\w\s]', '', normalized_text)
        tokens = self.text_processor.urdu_tokenize(cleaned_text)
        filtered_text = [token for token in tokens if token not in self.stopwords]
        lemmatized_text = self.text_processor.lemmatize_sentence(" ".join(filtered_text))
        return lemmatized_text, filtered_text

# Class for Ontology Management
class Content:
    @staticmethod
    def create_ontology_from_database():
        onto = get_ontology("http://example.org/universal_ontology.owl")

        with onto:
            class Topic(Thing): pass
            class Hadith(Thing): pass
            class Ayaat(Thing): pass

            class hasQuestion(DataProperty): domain = [Topic]; range = [str]
            class hasAnswer(DataProperty): domain = [Topic]; range = [str]
            class hasReference(DataProperty): domain = [Topic]; range = [str]
            class hasText(DataProperty): domain = [Hadith]; range = [str]

            TopicModel = apps.get_model("aichatbot", "Topic")
            QuestionModel = apps.get_model("aichatbot", "Question")
            AnswerModel = apps.get_model("aichatbot", "Answer")
            ReferenceModel = apps.get_model("aichatbot", "Reference")
            HadithModel = apps.get_model("aichatbot", "Hadith")
            AyaatModel = apps.get_model("aichatbot", "Ayaat")

            for topic in TopicModel.objects.all():
                ontology_topic = Topic(topic.name)
                ontology_topic.hasQuestion = [q.text for q in QuestionModel.objects.filter(topic=topic)]
                ontology_topic.hasAnswer = [a.text for a in AnswerModel.objects.filter(topic=topic)]
                ontology_topic.hasReference = [r.text for r in ReferenceModel.objects.filter(topic=topic)]

            for h in HadithModel.objects.all():
                ontology_hadith = Hadith(f"Hadith_{h.id}")
                ontology_hadith.hasText = [h.text]

            for ayah in AyaatModel.objects.all():
                ontology_ayah = Ayaat(f"Ayaat_{ayah.id}")
                ontology_ayah.hasAyahText = [ayah.text]

        onto.save(file="universal_ontology.owl", format="rdfxml")
        return onto

    @staticmethod
    def extract_topic_corpus(onto):
        return [instance.name for instance in onto.Topic.instances()]


class HadithSearcher:
    def __init__(self, ontology, text_processor):
        self.onto = ontology
        self.text_processor = text_processor
        self.hadiths = list(self.onto.Hadith.instances())

    def search(self, query):
        query = query.strip()
        query_parts = [part.strip() for part in query.split('|') if part.strip()]

        for hadith in self.hadiths:
            if hasattr(hadith, 'hasText') and hadith.hasText:
                hadith_text = hadith.hasText[0]

                # Check if query or parts appear in hadith text
                if (query in hadith_text) or any(part in hadith_text for part in query_parts) or all(part in hadith_text for part in query_parts):
                    # Get reference if exists
                    hadith_ref = ""
                    if hasattr(hadith, 'hasReference') and hadith.hasReference:
                        hadith_ref = hadith.hasReference[0]
                    return [(hadith_text, hadith_ref)]  # Return only the first match

        return []  # Return empty list if no match found


class AyaatSearcher:
    def __init__(self, ontology, text_processor):
        self.onto = ontology
        self.text_processor = text_processor
        self.ayaat = list(self.onto.Ayaat.instances())

    def search(self, query):
        query = query.strip()
        query_parts = [part.strip() for part in query.split('|') if part.strip()]
        matched_ayaat = []

        # Reference handling
        reference_query = None
        if "Reference:" in query and "حوالہ:" in query:
            for part in query_parts:
                if "Reference:" in part and "حوالہ:" in part:
                    reference_query = part
                    break

        for ayah in self.ayaat:
            if hasattr(ayah, 'hasAyahText') and ayah.hasAyahText:
                ayah_text = ayah.hasAyahText[0]
                reference = ""
                if hasattr(ayah, 'hasBookTitle') and ayah.hasBookTitle:
                    reference = ayah.hasBookTitle[0]

                # If exact reference is provided, match it directly
                if reference_query and reference_query.strip() == reference.strip():
                    matched_ayaat.append((ayah_text, reference))
                # Else match based on text parts
                elif (query in ayah_text) or any(part in ayah_text for part in query_parts) or all(part in ayah_text for part in query_parts):
                    matched_ayaat.append((ayah_text, reference))

        return matched_ayaat




# Query Handler Class
class QueryHandler:
    def __init__(self, onto, text_processor, query_history):
        self.onto = onto
        self.text_processor = text_processor
        self.query_history = query_history
        self.hadith_searcher = HadithSearcher(onto, text_processor)
        self.ayah_searcher = AyaatSearcher(onto, text_processor)


    def find_closest_topic_tfidf(self, question):
        processed_question, key_phrases = self.text_processor.preprocess_text_with_focus(question)
        corpus = Content.extract_topic_corpus(self.onto)
        preprocessed_corpus = [self.text_processor.preprocess_text(topic) for topic in corpus]

        if not preprocessed_corpus:
            return None, 0

        vectorizer = TfidfVectorizer()
        topic_vectors = vectorizer.fit_transform(preprocessed_corpus)
        query_vector = vectorizer.transform([processed_question])

        similarities = cosine_similarity(query_vector, topic_vectors).flatten()
        max_score_index = similarities.argmax()
        max_score = similarities[max_score_index]

        if max_score > 0.6:
            return list(self.onto.Topic.instances())[max_score_index], max_score
        return None, 0


    def highlight_keywords(self, text, keywords):
        for keyword in sorted(keywords, key=len, reverse=True):
            text = text.replace(keyword, f"<span class='highlight'>{keyword}</span>")
        return text

    def query_ontology(self, question):
        responses = []

        is_hadith_reference_query = bool(re.search(r'\d{2,4}', question))

        if is_hadith_reference_query:
            hadiths = self.hadith_searcher.search(question)
            if hadiths:
                formatted_hadiths = []
                for text, ref in hadiths:
                    if ref:
                        hadith_html = f"<div class='response-hadith'>{text}<br>Reference: {ref}</div>"
                    else:
                        hadith_html = f"<div class='response-hadith'>{text}</div>"
                    formatted_hadiths.append(hadith_html)
                return formatted_hadiths
            else:
                return ["معاف کیجئے، مجھے اس حدیث کا حوالہ نہیں ملا۔"]


        processed_question, key_phrases = self.text_processor.preprocess_text_with_focus(question)
        key_phrases_set = set(key_phrases)
        is_short_query = len(key_phrases_set) <= 2

        # Step 1: Try TF-IDF Matching (only if not very short)
        if not is_short_query:
            best_topic, best_score = self.find_closest_topic_tfidf(question)
            if best_topic and best_score > 0.75:
                responses.append(f'<div class="response-title">عنوان: {self.highlight_keywords(best_topic.name, key_phrases_set)}</div>')
                for q in set(best_topic.hasQuestion):
                    responses.append(f'<div class="response-question">سوال: {self.highlight_keywords(q, key_phrases_set)}</div>')
                for a in set(best_topic.hasAnswer):
                    responses.append(f'<div class="response-answer">جواب: {self.highlight_keywords(a, key_phrases_set)}</div>')
                for r in set(best_topic.hasReference):
                    hyperlink = f'<a href="#" class="reference-link" data-query="{self.highlight_keywords(r, key_phrases_set)}">Reference: {self.highlight_keywords(r, key_phrases_set)}</a>'
                    responses.append(hyperlink)
                return responses

        # Step 2: Keyword-based Matching (only return if real match found)
        matched_topics = []
        for topic in self.onto.Topic.instances():
            combined_text = self.text_processor.preprocess_text(topic.name)

            for q in topic.hasQuestion:
                combined_text += " " + self.text_processor.preprocess_text(q)
            for a in topic.hasAnswer:
                combined_text += " " + self.text_processor.preprocess_text(a)

            if key_phrases_set and all(k in combined_text for k in key_phrases_set):
                matched_topics.append(topic)

        if matched_topics:
            for topic in matched_topics:
                responses.append(f'<div class="response-title">عنوان: {self.highlight_keywords(topic.name, key_phrases_set)}</div>')
                for q in set(topic.hasQuestion):
                    responses.append(f'<div class="response-question">سوال: {self.highlight_keywords(q, key_phrases_set)}</div>')
                for a in set(topic.hasAnswer):
                    responses.append(f'<div class="response-answer">جواب: {self.highlight_keywords(a, key_phrases_set)}</div>')
                for r in set(topic.hasReference):
                    hyperlink = f'<a href="#" class="reference-link" data-query="{self.highlight_keywords(r, key_phrases_set)}">Reference: {self.highlight_keywords(r, key_phrases_set)}</a>'
                    responses.append(hyperlink)
            return responses

        # Hadith search agar topic match na ho
        hadiths = self.hadith_searcher.search(question)
        if hadiths:
            formatted_hadiths = []
            for text, ref in hadiths:
                if ref:
                    hadith_html = f"<div class='response-hadith'>{text}<br>Reference: {ref}</div>"
                else:
                    hadith_html = f"<div class='response-hadith'>{text}</div>"
                formatted_hadiths.append(hadith_html)
            return formatted_hadiths

        # Ayaat search if hadiths not found
        ayaat = self.ayah_searcher.search(question)
        if ayaat:
            formatted_ayaat = []
            for text, ref in ayaat:
                if ref:
                    ayah_html = f"<div class='response-ayah'>{text}<br>Reference: {ref}</div>"
                else:
                    ayah_html = f"<div class='response-ayah'>{text}</div>"
                formatted_ayaat.append(ayah_html)
            return formatted_ayaat


        # Agar hadith bhi match na hui
        return ["معاف کیجئے، مجھے اس سوال کا جواب نہیں معلوم۔"]



# Chatbot Class
class Chatbot:
    def __init__(self):
        self.onto = Content.create_ontology_from_database()
        self.text_processor = UrduTextProcessor()
        self.query_history = History()
        self.query_handler = QueryHandler(self.onto, self.text_processor, self.query_history)

    def start(self):
        print("یونیورسل اسلامی چیٹ بوٹ میں خوش آمدید!")
        while True:
            question = input("\nسوال کریں: ")
            if question.lower() == "exit":
                print("الوداع!")
                break
            responses = self.query_handler.query_ontology(question)
            for response in responses:
                print(f"- {response}")