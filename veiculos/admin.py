from django.contrib import admin

from .models import Marca, Veiculo, FotoVeiculo


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
    )

    search_fields = (
        "nome",
    )


class FotoVeiculoInline(admin.TabularInline):
    model = FotoVeiculo
    extra = 1


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):

    list_display = (
        "marca",
        "modelo",
        "ano",
        "valor",
        "quilometragem",
        "publicado",
        "destaque",
        "vendido",
    )

    list_filter = (
        "marca",
        "ano",
        "combustivel",
        "cambio",
        "publicado",
        "destaque",
        "vendido",
    )

    search_fields = (
        "modelo",
        "marca__nome",
    )

    list_editable = (
        "publicado",
        "destaque",
        "vendido",
    )

    inlines = [
        FotoVeiculoInline
    ]


@admin.register(FotoVeiculo)
class FotoVeiculoAdmin(admin.ModelAdmin):

    list_display = (
        "veiculo",
        "ordem",
    )

    list_filter = (
        "veiculo",
    )
