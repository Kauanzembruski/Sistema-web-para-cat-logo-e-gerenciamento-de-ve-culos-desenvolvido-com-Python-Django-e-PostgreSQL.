import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from veiculos.models import FotoVeiculo, Marca, Veiculo


class PainelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_root = tempfile.mkdtemp()
        cls._override_media = override_settings(MEDIA_ROOT=cls._media_root)
        cls._override_media.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override_media.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="kauan",
            password="senha-segura",
            first_name="Kauan",
            is_staff=True,
        )
        self.client.force_login(self.usuario)

    def _imagem_upload(self, nome):
        return SimpleUploadedFile(
            nome,
            (
                b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
                b"\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x00\x00\x00\x00"
                b"\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02"
                b"\x44\x01\x00\x3b"
            ),
            content_type="image/gif",
        )

    def test_painel_exige_login(self):
        self.client.logout()

        response = self.client.get(reverse("painel:dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("painel:login"), response["Location"])
        self.assertIn("next=/painel/", response["Location"])

    def test_login_autentica_usuario(self):
        self.client.logout()

        get_response = self.client.get(reverse("painel:login"))
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Entrar no painel")

        response = self.client.post(
            reverse("painel:login"),
            {
                "username": "kauan",
                "password": "senha-segura",
            },
        )

        self.assertRedirects(response, reverse("painel:dashboard"))

    def test_dashboard_renderiza_tela_inicial(self):
        response = self.client.get(reverse("painel:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Boa noite, Kauan.")
        self.assertContains(response, '<span class="panel-avatar" aria-hidden="true">K</span>', html=True)
        self.assertContains(response, "Administrador")
        self.assertContains(response, reverse("painel:logout"))
        self.assertContains(response, "Visão geral")
        self.assertContains(response, "Veículos recentes")
        self.assertContains(response, "painel.css")

    def test_dashboard_exibe_totais_reais_de_veiculos(self):
        marca = Marca.objects.create(nome="Porsche")
        Veiculo.objects.create(
            slug="porsche-publicado",
            marca=marca,
            modelo="911",
            valor=1000000,
            ano=2020,
            quilometragem=0,
            cor="Prata",
            combustivel="Gasolina",
            cambio="Automatico",
            publicado=True,
        )
        Veiculo.objects.create(
            slug="porsche-rascunho",
            marca=marca,
            modelo="Macan",
            valor=700000,
            ano=2019,
            quilometragem=10000,
            cor="Azul",
            combustivel="Alcool",
            cambio="Manual",
            publicado=False,
        )

        response = self.client.get(reverse("painel:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_veiculos"], 2)
        self.assertEqual(response.context["total_publicados"], 1)
        self.assertEqual(response.context["total_rascunhos"], 1)
        self.assertContains(response, "<strong>2</strong>", html=True)
        self.assertContains(response, "<strong>1</strong>", html=True)

    def test_dashboard_exibe_veiculos_recentes_com_imagem_e_status(self):
        marca = Marca.objects.create(nome="Porsche")
        publicado = Veiculo.objects.create(
            slug="porsche-macan-painel",
            marca=marca,
            modelo="Macan",
            valor=700000,
            ano=2019,
            quilometragem=10000,
            cor="Azul",
            combustivel="Alcool",
            cambio="Manual",
            publicado=True,
        )
        rascunho = Veiculo.objects.create(
            slug="porsche-911-painel",
            marca=marca,
            modelo="911",
            valor=1000000,
            ano=2020,
            quilometragem=0,
            cor="Prata",
            combustivel="Gasolina",
            cambio="Automatico",
            publicado=False,
        )
        FotoVeiculo.objects.create(
            veiculo=publicado,
            imagem="veiculos/macan-painel.jpg",
            ordem=1,
        )

        response = self.client.get(reverse("painel:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/media/veiculos/macan-painel.jpg")
        self.assertContains(response, "Porsche Macan")
        self.assertContains(response, "Porsche 911")
        self.assertContains(response, "Publicado")
        self.assertContains(response, "Rascunho")
        self.assertContains(response, reverse("painel:veiculo_editar", kwargs={"slug": publicado.slug}))
        self.assertContains(response, reverse("painel:veiculo_excluir", kwargs={"slug": publicado.slug}))
        self.assertNotContains(response, "A8C1D23")
        self.assertNotContains(response, "XYZ9A87")
        self.assertIn(rascunho, response.context["veiculos_recentes"])
        self.assertIn(publicado, response.context["veiculos_recentes"])

    def test_dashboard_lista_todos_os_veiculos(self):
        marca = Marca.objects.create(nome="Toyota")

        for indice in range(5):
            Veiculo.objects.create(
                slug=f"toyota-hilux-{indice}",
                marca=marca,
                modelo=f"Hilux {indice}",
                valor=280000,
                ano=2018 + indice,
                quilometragem=1000,
                cor="Branco",
                combustivel="Diesel",
                cambio="Automatico",
                publicado=indice % 2 == 0,
            )

        response = self.client.get(reverse("painel:dashboard"))
        veiculos_recentes = list(response.context["veiculos_recentes"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(veiculos_recentes), 5)

        for indice in range(5):
            self.assertContains(response, f"Toyota Hilux {indice}")

    def test_secao_veiculos_lista_busca_e_filtra(self):
        porsche = Marca.objects.create(nome="Porsche")
        toyota = Marca.objects.create(nome="Toyota")
        macan = Veiculo.objects.create(
            slug="porsche-macan-lista",
            marca=porsche,
            modelo="Macan",
            valor=700000,
            ano=2019,
            quilometragem=10000,
            cor="Azul",
            combustivel="Gasolina",
            cambio="Automatico",
            publicado=True,
        )
        hilux = Veiculo.objects.create(
            slug="toyota-hilux-lista",
            marca=toyota,
            modelo="Hilux",
            valor=280000,
            ano=2020,
            quilometragem=25000,
            cor="Branco",
            combustivel="Diesel",
            cambio="Automatico",
            publicado=False,
        )

        response = self.client.get(reverse("painel:veiculos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Porsche Macan")
        self.assertContains(response, "Toyota Hilux")
        self.assertContains(response, reverse("painel:veiculo_criar"))
        self.assertIn(macan, response.context["veiculos"])
        self.assertIn(hilux, response.context["veiculos"])

        busca_response = self.client.get(reverse("painel:veiculos"), {"busca": "macan"})
        self.assertContains(busca_response, "Porsche Macan")
        self.assertNotContains(busca_response, "Toyota Hilux")

        filtro_response = self.client.get(reverse("painel:veiculos"), {"status": "rascunhos"})
        self.assertContains(filtro_response, "Toyota Hilux")
        self.assertNotContains(filtro_response, "Porsche Macan")

    def test_formulario_novo_veiculo_renderiza(self):
        Marca.objects.create(nome="Porsche")

        response = self.client.get(reverse("painel:veiculo_criar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cadastrar veículo")
        self.assertContains(response, "Informações")
        self.assertContains(response, "Publicação")
        self.assertContains(response, '<select name="marca"', html=False)
        self.assertContains(response, "Porsche")
        self.assertContains(response, 'name="modelo"')
        self.assertContains(response, 'name="foto"')
        self.assertContains(response, "Fotos do veículo")
        self.assertContains(response, "multiple")
        self.assertContains(response, "data-photo-upload")

    def test_formulario_novo_veiculo_cria_registro(self):
        marca = Marca.objects.create(nome="Porsche")

        response = self.client.post(
            reverse("painel:veiculo_criar"),
            {
                "marca": str(marca.id),
                "modelo": "Cayenne",
                "valor": "850000.00",
                "ano": "2022",
                "quilometragem": "15000",
                "cor": "Preto",
                "combustivel": "Gasolina",
                "cambio": "Automatico",
                "descricao": "SUV premium",
                "publicado": "on",
                "destaque": "on",
            },
        )

        self.assertRedirects(response, reverse("painel:dashboard"))
        veiculo = Veiculo.objects.get(modelo="Cayenne")
        self.assertEqual(veiculo.marca.nome, "Porsche")
        self.assertEqual(veiculo.slug, "porsche-cayenne-2022")
        self.assertTrue(veiculo.publicado)
        self.assertTrue(veiculo.destaque)
        self.assertFalse(veiculo.vendido)

    def test_formulario_novo_veiculo_salva_multiplas_fotos(self):
        marca = Marca.objects.create(nome="Porsche")

        response = self.client.post(
            reverse("painel:veiculo_criar"),
            {
                "marca": str(marca.id),
                "modelo": "Panamera",
                "valor": "900000.00",
                "ano": "2023",
                "quilometragem": "8000",
                "cor": "Cinza",
                "combustivel": "Gasolina",
                "cambio": "Automatico",
                "descricao": "Executive",
                "publicado": "on",
                "foto": [
                    self._imagem_upload("frente.gif"),
                    self._imagem_upload("traseira.gif"),
                ],
            },
        )

        self.assertRedirects(response, reverse("painel:dashboard"))
        veiculo = Veiculo.objects.get(modelo="Panamera")
        fotos = list(veiculo.fotos.order_by("ordem"))
        self.assertEqual(len(fotos), 2)
        self.assertEqual([foto.ordem for foto in fotos], [1, 2])

    def test_formulario_edita_veiculo(self):
        porsche = Marca.objects.create(nome="Porsche")
        toyota = Marca.objects.create(nome="Toyota")
        veiculo = Veiculo.objects.create(
            slug="porsche-macan-2019",
            marca=porsche,
            modelo="Macan",
            valor=700000,
            ano=2019,
            quilometragem=10000,
            cor="Azul",
            combustivel="Alcool",
            cambio="Manual",
            publicado=True,
        )

        get_response = self.client.get(reverse("painel:veiculo_editar", kwargs={"slug": veiculo.slug}))
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Editar veículo")
        self.assertContains(get_response, "Salvar alterações")

        response = self.client.post(
            reverse("painel:veiculo_editar", kwargs={"slug": veiculo.slug}),
            {
                "marca": str(toyota.id),
                "modelo": "Hilux",
                "valor": "280000.00",
                "ano": "2020",
                "quilometragem": "25000",
                "cor": "Branco",
                "combustivel": "Diesel",
                "cambio": "Automatico",
                "descricao": "SRX",
                "vendido": "on",
            },
        )

        self.assertRedirects(response, reverse("painel:dashboard"))
        veiculo.refresh_from_db()
        self.assertEqual(veiculo.marca, toyota)
        self.assertEqual(veiculo.modelo, "Hilux")
        self.assertEqual(veiculo.slug, "toyota-hilux-2020")
        self.assertFalse(veiculo.publicado)
        self.assertTrue(veiculo.vendido)

    def test_formulario_edita_veiculo_anexa_multiplas_fotos(self):
        marca = Marca.objects.create(nome="Porsche")
        veiculo = Veiculo.objects.create(
            slug="porsche-macan-fotos",
            marca=marca,
            modelo="Macan",
            valor=700000,
            ano=2019,
            quilometragem=10000,
            cor="Azul",
            combustivel="Gasolina",
            cambio="Automatico",
            publicado=True,
        )
        FotoVeiculo.objects.create(veiculo=veiculo, imagem="veiculos/atual.jpg", ordem=1)

        response = self.client.post(
            reverse("painel:veiculo_editar", kwargs={"slug": veiculo.slug}),
            {
                "marca": str(marca.id),
                "modelo": "Macan",
                "valor": "700000.00",
                "ano": "2019",
                "quilometragem": "10000",
                "cor": "Azul",
                "combustivel": "Gasolina",
                "cambio": "Automatico",
                "descricao": "Turbo",
                "publicado": "on",
                "foto": [
                    self._imagem_upload("interior.gif"),
                    self._imagem_upload("painel.gif"),
                ],
            },
        )

        self.assertRedirects(response, reverse("painel:dashboard"))
        fotos = list(veiculo.fotos.order_by("ordem"))
        self.assertEqual(len(fotos), 3)
        self.assertEqual([foto.ordem for foto in fotos], [1, 2, 3])

    def test_exclui_veiculo_com_confirmacao(self):
        marca = Marca.objects.create(nome="Porsche")
        veiculo = Veiculo.objects.create(
            slug="porsche-911-2020",
            marca=marca,
            modelo="911",
            valor=1000000,
            ano=2020,
            quilometragem=0,
            cor="Prata",
            combustivel="Gasolina",
            cambio="Automatico",
        )

        get_response = self.client.get(reverse("painel:veiculo_excluir", kwargs={"slug": veiculo.slug}))
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Excluir veículo")
        self.assertTrue(Veiculo.objects.filter(id=veiculo.id).exists())

        response = self.client.post(reverse("painel:veiculo_excluir", kwargs={"slug": veiculo.slug}))

        self.assertRedirects(response, reverse("painel:dashboard"))
        self.assertFalse(Veiculo.objects.filter(id=veiculo.id).exists())
