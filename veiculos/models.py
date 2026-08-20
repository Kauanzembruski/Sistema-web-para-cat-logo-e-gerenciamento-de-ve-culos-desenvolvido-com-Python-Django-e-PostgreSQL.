from django.db import models
from django.conf import settings

# Create your models here.
class Marca(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Veiculo(models.Model):

    slug = models.SlugField(max_length=200,unique=True)
    marca = models.ForeignKey(Marca,on_delete=models.PROTECT,related_name="veiculos" )
    modelo = models.CharField( max_length=150)
    valor = models.DecimalField(max_digits=10,decimal_places=2)
    ano = models.PositiveIntegerField()
    quilometragem = models.PositiveIntegerField(default=0)
    cor = models.CharField(max_length=50)
    combustivel = models.CharField(max_length=30)
    cambio = models.CharField(max_length=30)
    descricao = models.TextField(blank=True)
    publicado = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    vendido = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.ano}"

    @property
    def foto_principal(self):
        fotos_carregadas = getattr(self, "_prefetched_objects_cache", {}).get("fotos")

        if fotos_carregadas is not None:
            return next(iter(fotos_carregadas), None)

        return self.fotos.order_by("ordem", "id").first()

    @property
    def imagem(self):
        foto = self.foto_principal

        if foto and foto.imagem:
            try:
                return foto.imagem.url
            except ValueError:
                pass

        return f"{settings.STATIC_URL}img/vehicle-placeholder.svg"

    @property
    def alt(self):
        return f"{self.marca} {self.modelo} {self.ano}"

    @property
    def versao(self):
        if self.descricao:
            return self.descricao

        return f"Cor {self.cor}"

    @property
    def km(self):
        return f"{self.quilometragem:,}".replace(",", ".") + " km"

    @property
    def preco(self):
        valor = f"{self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {valor}"


class FotoVeiculo(models.Model):

    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.CASCADE,
        related_name="fotos"
    )

    imagem = models.ImageField(
        upload_to="veiculos/"
    )

    ordem = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"Foto - {self.veiculo}"

    class Meta:
        ordering = ("ordem", "id")
