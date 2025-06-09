from django.contrib import admin
from .models import Topic, Book, Question, Answer, Hadith, Reference, Ayaat, CustomUser
from django.contrib.auth.admin import UserAdmin


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display topic name in the admin list


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title',)  # Show book titles in admin list


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('book', 'topic', 'text_preview')  # Show book, topic, and text preview

    def text_preview(self, obj):
        return obj.text[:50]  # Display the first 50 characters of the text
    text_preview.short_description = 'Text Preview'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('book', 'topic', 'text_preview')  # Show book, topic, and text preview

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Text Preview'


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('book', 'topic', 'text_preview')  # Show book, topic, and text preview

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Text Preview'


@admin.register(Hadith)
class HadithAdmin(admin.ModelAdmin):
    list_display = ('book', 'text_preview')  # Show book and text preview

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Text Preview'


@admin.register(Ayaat)
class AyaatAdmin(admin.ModelAdmin):
    list_display = ('book', 'text_preview')  # Show book and text preview

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Text Preview'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'mobile', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('mobile',)}),
    )
