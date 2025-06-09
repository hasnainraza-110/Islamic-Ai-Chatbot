from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from aichatbot import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path("home/", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", LogoutView.as_view(next_page='/'), name="logout"),
    path('chatbot/', views.chatbot_view, name='chatbot_view'),
]
