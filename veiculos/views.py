from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Marca, Veiculo


def home(request):
    destaques = (
        Veiculo.objects
        .filter(publicado=True, destaque=True)
        .select_related("marca")
        .prefetch_related("fotos")
        .order_by("-criado_em")
    )

    return render(
        request,
        "veiculos/home.html",
        {
            "active_page": "home",
            "destaques": destaques,
        },
    )


def catalogo(request):
    filtros = {
        "busca": request.GET.get("busca", "").strip(),
        "marca": request.GET.get("marca", "").strip(),
        "modelo": request.GET.get("modelo", "").strip(),
        "ano": request.GET.get("ano", "").strip(),
        "cambio": request.GET.get("cambio", "").strip(),
        "combustivel": request.GET.get("combustivel", "").strip(),
        "ordenacao": request.GET.get("ordenacao", "recentes").strip() or "recentes",
    }

    veiculos = (
        Veiculo.objects
        .filter(publicado=True)
        .select_related("marca")
        .prefetch_related("fotos")
    )

    if filtros["busca"]:
        veiculos = veiculos.filter(
            Q(modelo__icontains=filtros["busca"])
            | Q(marca__nome__icontains=filtros["busca"])
            | Q(cor__icontains=filtros["busca"])
            | Q(descricao__icontains=filtros["busca"])
        )

    if filtros["marca"] and filtros["marca"] != "todas":
        veiculos = veiculos.filter(marca__nome=filtros["marca"])

    if filtros["modelo"] and filtros["modelo"] != "todos":
        veiculos = veiculos.filter(modelo=filtros["modelo"])

    if filtros["ano"] and filtros["ano"] != "todos":
        veiculos = veiculos.filter(ano=filtros["ano"])

    if filtros["cambio"] and filtros["cambio"] != "todos":
        veiculos = veiculos.filter(cambio=filtros["cambio"])

    if filtros["combustivel"] and filtros["combustivel"] != "todos":
        veiculos = veiculos.filter(combustivel=filtros["combustivel"])

    ordenacoes = {
        "recentes": "-criado_em",
        "menor-preco": "valor",
        "maior-preco": "-valor",
        "menor-km": "quilometragem",
        "maior-km": "-quilometragem",
    }
    veiculos = veiculos.order_by(ordenacoes.get(filtros["ordenacao"], "-criado_em"))

    total_encontrados = veiculos.count()
    paginador = Paginator(veiculos, 8)
    pagina = paginador.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "veiculos/catalogo.html",
        {
            "active_page": "catalogo",
            "veiculos": pagina.object_list,
            "pagina": pagina,
            "query_string": query_params.urlencode(),
            "total_encontrados": total_encontrados,
            "filtros": filtros,
            "marcas": Marca.objects.filter(veiculos__publicado=True).distinct().order_by("nome"),
            "modelos": (
                Veiculo.objects
                .filter(publicado=True)
                .order_by("modelo")
                .values_list("modelo", flat=True)
                .distinct()
            ),
            "anos": (
                Veiculo.objects
                .filter(publicado=True)
                .order_by("-ano")
                .values_list("ano", flat=True)
                .distinct()
            ),
            "cambios": (
                Veiculo.objects
                .filter(publicado=True)
                .order_by("cambio")
                .values_list("cambio", flat=True)
                .distinct()
            ),
            "combustiveis": (
                Veiculo.objects
                .filter(publicado=True)
                .order_by("combustivel")
                .values_list("combustivel", flat=True)
                .distinct()
            ),
        }
    )

def detalhe(request, slug):

    veiculo = get_object_or_404(
        Veiculo.objects.select_related("marca").prefetch_related("fotos"),
        slug=slug,
        publicado=True,
    )

    return render(
        request,
        "veiculos/detalhe.html",
        {
            "active_page": "catalogo",
            "veiculo": veiculo,
        }
    )
