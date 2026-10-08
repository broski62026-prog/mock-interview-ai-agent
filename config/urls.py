from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def home(request):
    return redirect("login")


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", home, name="home"),

    path("", include("accounts.urls")),
    path("", include("interviews.urls")),
]