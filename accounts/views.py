from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        error = "Invalid username or password."

    return render(
        request,
        "login.html",
        {"error": error}
    )


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):

    response = requests.get(
        "http://127.0.0.1:8001/"
    )

    fastapi_message = response.json()["message"]

    return render(
        request,
        "dashboard.html",
        {
            "fastapi_message": fastapi_message
        }
    )