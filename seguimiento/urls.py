from django.urls import path

from . import views

urlpatterns = [
    path("", views.subir_rfq, name="subir_rfq"),
    path("confirmar/", views.confirmar, name="confirmar"),
    path("historial/", views.historial, name="historial"),
    path("historial/exportar.csv", views.exportar_historial_csv, name="exportar_historial_csv"),
    path("estado/", views.estado, name="estado"),
]
