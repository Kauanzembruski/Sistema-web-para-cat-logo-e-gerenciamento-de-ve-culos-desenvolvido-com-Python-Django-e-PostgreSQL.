from django.urls import path

from . import views

app_name = "painel"

urlpatterns = [
    path("login/", views.painel_login, name="login"),
    path("logout/", views.painel_logout, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("veiculos/", views.veiculos, name="veiculos"),
    path("veiculos/novo/", views.veiculo_criar, name="veiculo_criar"),
    path("veiculos/<slug:slug>/editar/", views.veiculo_editar, name="veiculo_editar"),
    path("veiculos/<slug:slug>/excluir/", views.veiculo_excluir, name="veiculo_excluir"),
]
