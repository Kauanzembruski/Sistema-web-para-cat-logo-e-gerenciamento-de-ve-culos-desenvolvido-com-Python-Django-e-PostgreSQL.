from django.urls import path

from . import views

app_name = "veiculos"

urlpatterns = [
    path("", views.home, name="home"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("veiculo/<slug:slug>/", views.detalhe, name="detalhe"),
]
