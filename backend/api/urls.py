from django.urls import path

from .views import health, plan

urlpatterns = [
    path("health", health, name="health"),
    path("plan", plan, name="plan"),
]
