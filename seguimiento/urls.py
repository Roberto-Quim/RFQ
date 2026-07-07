from django.urls import path

from . import views

urlpatterns = [
    path("", views.subir_rfq, name="subir_rfq"),
    path("confirmar/", views.confirmar, name="confirmar"),
    path("historial/", views.historial, name="historial"),
]
