from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("plzgg/", views.plzgg, name="plzgg"),
    path("plzgg/forms/", views.forms, name="forms"),
]