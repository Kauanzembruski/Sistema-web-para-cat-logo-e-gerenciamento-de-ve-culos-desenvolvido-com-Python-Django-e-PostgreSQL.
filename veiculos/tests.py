from django.test import TestCase, override_settings
from django.urls import reverse

from .models import FotoVeiculo, Marca, Veiculo


@override_settings(ALLOWED_HOSTS=["testserver"])
class CatalogoTests(TestCase):
    def setUp(self):
        fiat = Marca.objects.create(nome="FIAT")
        porsche = Marca.objects.create(nome="PORSCHE")

        self.toro = Veiculo.objects.create(
            slug="fiat-toro",
            marca=fiat,
            modelo="Toro",
            valor=120000,
            ano=2024,
            quilometragem=18000,
            cor="Prata",
            combustivel="Flex",
            cambio="Automatico",
            descricao="Volcano",
        )
        FotoVeiculo.objects.create(
            veiculo=self.toro,
            imagem="veiculos/toro.jpg",
            ordem=1,
        )

        self.boxster = Veiculo.objects.create(
            slug="porsche-boxster",
            marca=porsche,
            modelo="Boxster",
            valor=280000,
            ano=2021,
            quilometragem=9000,
            cor="Branco",
            combustivel="Gasolina",
            cambio="Automatico",
        )

    def test_home_renderiza_hero_inicial(self):
        response = self.client.get(reverse("veiculos:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home-hero")
        self.assertContains(response, "background_home.png")
        self.assertContains(response, "Ver catálogo")
        self.assertContains(response, "fim_home.png")
        self.assertContains(response, "home-footer")
        self.assertNotContains(response, "catalog-board")

    def test_home_exibe_apenas_veiculos_em_destaque(self):
        self.toro.destaque = True
        self.toro.save(update_fields=["destaque"])

        response = self.client.get(reverse("veiculos:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home-featured")
        self.assertContains(response, "Veículos que se destacam.")
        self.assertContains(response, "Toro")
        self.assertNotContains(response, "Boxster")

    def test_home_exibe_seta_quando_tem_mais_de_quatro_destaques(self):
        marca = Marca.objects.create(nome="BMW")
        for indice in range(5):
            Veiculo.objects.create(
                slug=f"bmw-destaque-{indice}",
                marca=marca,
                modelo=f"Destaque {indice}",
                valor=200000 + indice,
                ano=2024,
                quilometragem=1000,
                cor="Preto",
                combustivel="Gasolina",
                cambio="Automatico",
                destaque=True,
            )

        response = self.client.get(reverse("veiculos:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-featured-next')

    def test_catalogo_continua_em_url_propria(self):
        response = self.client.get(reverse("veiculos:catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "catalog-board")
        self.assertContains(response, "Catálogo de Veículos")

    def test_catalogo_renderiza_imagem_principal_e_total(self):
        response = self.client.get(reverse("veiculos:catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/media/veiculos/toro.jpg")
        self.assertContains(response, "2 veículos encontrados")

    def test_catalogo_filtra_por_busca(self):
        response = self.client.get(reverse("veiculos:catalogo"), {"busca": "toro"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FIAT Toro")
        self.assertNotContains(response, "PORSCHE Boxster")

    def test_catalogo_ordena_por_menor_quilometragem(self):
        response = self.client.get(
            reverse("veiculos:catalogo"),
            {"ordenacao": "menor-km"},
        )

        self.assertEqual(response.status_code, 200)
        veiculos = list(response.context["veiculos"])
        self.assertEqual(veiculos, [self.boxster, self.toro])

    def test_catalogo_ordena_por_maior_quilometragem(self):
        response = self.client.get(
            reverse("veiculos:catalogo"),
            {"ordenacao": "maior-km"},
        )

        self.assertEqual(response.status_code, 200)
        veiculos = list(response.context["veiculos"])
        self.assertEqual(veiculos, [self.toro, self.boxster])

    def test_catalogo_ordena_por_preco(self):
        response_menor = self.client.get(
            reverse("veiculos:catalogo"),
            {"ordenacao": "menor-preco"},
        )
        response_maior = self.client.get(
            reverse("veiculos:catalogo"),
            {"ordenacao": "maior-preco"},
        )

        self.assertEqual(list(response_menor.context["veiculos"]), [self.toro, self.boxster])
        self.assertEqual(list(response_maior.context["veiculos"]), [self.boxster, self.toro])

    def test_catalogo_exibe_limpar_filtros(self):
        response = self.client.get(reverse("veiculos:catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Filtrar veículos")
        self.assertContains(response, "Limpar filtros")

    def test_catalogo_exibe_modal_de_filtros(self):
        response = self.client.get(reverse("veiculos:catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="ordenacao" data-sort-select onchange="this.form.submit()"')
        self.assertContains(response, 'id="catalog-filter-modal"')
        self.assertContains(response, 'name="marca"')
        self.assertContains(response, 'name="modelo"')
        self.assertContains(response, "Aplicar filtros")

    def test_detalhe_inexistente_retorna_404(self):
        response = self.client.get(
            reverse("veiculos:detalhe", kwargs={"slug": "nao-existe"}),
        )

        self.assertEqual(response.status_code, 404)
