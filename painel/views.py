from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import slugify

from veiculos.models import FotoVeiculo, Veiculo

from .forms import VeiculoForm


def painel_login(request):
    if request.user.is_authenticated:
        return redirect("painel:dashboard")

    next_url = request.POST.get("next") or request.GET.get("next") or reverse("painel:dashboard")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("painel:dashboard")

    context = {"next": next_url}

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)

        context["error"] = "Usuário ou senha inválidos."
        context["username"] = username

    return render(request, "painel/login.html", context)


@login_required(login_url="painel:login")
def painel_logout(request):
    logout(request)
    return redirect("painel:login")


@login_required(login_url="painel:login")
def dashboard(request):
    total_veiculos = Veiculo.objects.count()
    total_publicados = Veiculo.objects.filter(publicado=True).count()
    total_rascunhos = Veiculo.objects.filter(publicado=False).count()
    veiculos_recentes = (
        Veiculo.objects
        .select_related("marca")
        .prefetch_related("fotos")
        .order_by("-criado_em", "-id")
    )

    return render(
        request,
        "painel/dashboard.html",
        {
            "active_page": "dashboard",
            "total_veiculos": total_veiculos,
            "total_publicados": total_publicados,
            "total_rascunhos": total_rascunhos,
            "veiculos_recentes": veiculos_recentes,
        },
    )


@login_required(login_url="painel:login")
def veiculos(request):
    filtros = {
        "busca": request.GET.get("busca", "").strip(),
        "status": request.GET.get("status", "todos").strip() or "todos",
    }
    lista_veiculos = (
        Veiculo.objects
        .select_related("marca")
        .prefetch_related("fotos")
        .order_by("-criado_em", "-id")
    )

    if filtros["busca"]:
        lista_veiculos = lista_veiculos.filter(
            Q(modelo__icontains=filtros["busca"])
            | Q(marca__nome__icontains=filtros["busca"])
            | Q(cor__icontains=filtros["busca"])
            | Q(ano__icontains=filtros["busca"])
        )

    if filtros["status"] == "publicados":
        lista_veiculos = lista_veiculos.filter(publicado=True)
    elif filtros["status"] == "rascunhos":
        lista_veiculos = lista_veiculos.filter(publicado=False)
    elif filtros["status"] == "vendidos":
        lista_veiculos = lista_veiculos.filter(vendido=True)
    elif filtros["status"] == "destaques":
        lista_veiculos = lista_veiculos.filter(destaque=True)

    return render(
        request,
        "painel/veiculos.html",
        {
            "active_page": "veiculos",
            "filtros": filtros,
            "veiculos": lista_veiculos,
        },
    )


def _gerar_slug_unico(marca, modelo, ano, veiculo_id=None):
    base_slug = slugify(f"{marca} {modelo} {ano}") or "veiculo"
    slug = base_slug
    contador = 2

    slugs_existentes = Veiculo.objects.filter(slug=slug)
    if veiculo_id:
        slugs_existentes = slugs_existentes.exclude(id=veiculo_id)

    while slugs_existentes.exists():
        slug = f"{base_slug}-{contador}"
        contador += 1
        slugs_existentes = Veiculo.objects.filter(slug=slug)
        if veiculo_id:
            slugs_existentes = slugs_existentes.exclude(id=veiculo_id)

    return slug


def _salvar_fotos_veiculo(veiculo, fotos):
    if not fotos:
        return

    ultima_ordem = veiculo.fotos.order_by("-ordem", "-id").values_list("ordem", flat=True).first() or 0

    for indice, foto in enumerate(fotos, start=1):
        FotoVeiculo.objects.create(
            veiculo=veiculo,
            imagem=foto,
            ordem=ultima_ordem + indice,
        )


@login_required(login_url="painel:login")
def veiculo_criar(request):
    if request.method == "POST":
        form = VeiculoForm(request.POST, request.FILES)

        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.slug = _gerar_slug_unico(veiculo.marca.nome, veiculo.modelo, veiculo.ano)
            veiculo.save()

            _salvar_fotos_veiculo(veiculo, form.cleaned_data.get("foto"))

            return redirect("painel:dashboard")
    else:
        form = VeiculoForm(initial={"publicado": True})

    return render(
        request,
        "painel/veiculo_form.html",
        {
            "active_page": "veiculos",
            "form": form,
            "form_action": "painel:veiculo_criar",
            "page_title": "Cadastrar veículo",
            "page_subtitle": "Adicione um novo veículo ao catálogo.",
            "submit_label": "Salvar veículo",
        },
    )


@login_required(login_url="painel:login")
def veiculo_editar(request, slug):
    veiculo = get_object_or_404(
        Veiculo.objects.select_related("marca").prefetch_related("fotos"),
        slug=slug,
    )

    if request.method == "POST":
        form = VeiculoForm(request.POST, request.FILES, instance=veiculo)

        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.slug = _gerar_slug_unico(veiculo.marca.nome, veiculo.modelo, veiculo.ano, veiculo_id=veiculo.id)
            veiculo.save()

            _salvar_fotos_veiculo(veiculo, form.cleaned_data.get("foto"))

            return redirect("painel:dashboard")
    else:
        form = VeiculoForm(instance=veiculo)

    return render(
        request,
        "painel/veiculo_edit_form.html",
        {
            "active_page": "veiculos",
            "form": form,
            "veiculo": veiculo,
        },
    )


@login_required(login_url="painel:login")
def veiculo_excluir(request, slug):
    veiculo = get_object_or_404(Veiculo.objects.select_related("marca"), slug=slug)

    if request.method == "POST":
        veiculo.delete()
        return redirect("painel:dashboard")

    return render(
        request,
        "painel/veiculo_confirm_delete.html",
        {
            "active_page": "veiculos",
            "veiculo": veiculo,
        },
    )
