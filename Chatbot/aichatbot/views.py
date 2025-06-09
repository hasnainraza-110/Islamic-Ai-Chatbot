from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import CustomUser
from django.http import JsonResponse
from .final_chatbot import Chatbot
import json

# Initialize the chatbot with the ontology file
chatbot = Chatbot()

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        mobile = request.POST.get('mobile', '').strip()  

        if not (first_name and last_name and email and password and confirm_password and mobile):
            messages.error(request, "All fields are required!")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "User already registered with this email!")
            return redirect('register')

        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mobile=mobile  # Add the mobile number to the user creation
        )
        user.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect to home page after successful login
        else:
            messages.error(request, "Invalid email or password. Please try again.")

    return render(request, "login.html")


def index(request):
    """
    Renders the home page for the chatbot.
    """
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')


def chatbot_view(request):
    """
    Handles POST requests from the chatbot interface.
    Processes the user's query and returns the chatbot's response.
    """
    if request.method == "POST":
        try:
            # Get the data from the request body (JSON)
            data = json.loads(request.body)
            user_input = data.get("query", "").strip()

            if not user_input:
                return JsonResponse({"response": ["براہ کرم سوال درج کریں۔"]})

            # Generate the chatbot response
            responses = chatbot.query_handler.query_ontology(user_input)

            if not responses:
                return JsonResponse({"response": ["معاف کیجئے گا، کوئی جواب دستیاب نہیں۔"]})

            return JsonResponse({"response": responses})
        except Exception as e:
            # Handle errors gracefully
            return JsonResponse({"response": ["معاف کیجئے گا، کوئی خرابی پیش آگئی ہے۔"]}, status=500)

    return JsonResponse({"response": ["Invalid request method."]}, status=405)


def refresh_chatbot(request):
    """
    Refresh the chatbot ontology to include newly added data.
    """
    try:
        chatbot.refresh_ontology()
        return JsonResponse({"message": "Chatbot ontology refreshed successfully."})
    except Exception as e: 
        return JsonResponse({"message": "Failed to refresh chatbot ontology.", "error": str(e)}, status=500)
