from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=15, blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)

    def __str__(self):
        return self.username


class Book(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)  # عنوان / ٹاپک کا نام

    def __str__(self):
        return self.name


class Question(models.Model):
    book = models.ForeignKey(Book, related_name='questions', on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(Topic, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"سوال ({self.topic.name}): {self.text[:50]}"


class Answer(models.Model):
    book = models.ForeignKey(Book, related_name='answers', on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(Topic, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"جواب ({self.topic.name}): {self.text[:50]}"


class Reference(models.Model):
    book = models.ForeignKey(Book, related_name='references', on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(Topic, related_name='references', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"حوالہ ({self.topic.name}): {self.text[:50]}"


class Hadith(models.Model):
    book = models.ForeignKey(Book, related_name='hadiths', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()

    def __str__(self):
        return f"حدیث: {self.text[:50]}"


class Ayaat(models.Model):
    book = models.ForeignKey(Book, related_name='ayaat', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()

    def __str__(self):
        return f"آیت: {self.text[:50]}"
