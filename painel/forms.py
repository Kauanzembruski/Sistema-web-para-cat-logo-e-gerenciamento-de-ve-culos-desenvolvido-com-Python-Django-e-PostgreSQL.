from django import forms

from veiculos.models import Marca, Veiculo


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            return [super(MultipleImageField, self).clean(item, initial) for item in data]

        return [super().clean(data, initial)]


class VeiculoForm(forms.ModelForm):
    foto = MultipleImageField(
        label="Fotos do veículo",
        required=False,
        widget=MultipleImageInput(
            attrs={
                "accept": "image/*",
                "class": "photo-upload-input",
                "multiple": True,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["marca"].queryset = Marca.objects.order_by("nome")
        self.fields["marca"].empty_label = "Selecione a marca"
        self.fields["valor"].label = "Preço"
        self.fields["ano"].label = "Ano modelo"
        self.fields["descricao"].label = "Versão"

    class Meta:
        model = Veiculo
        fields = (
            "marca",
            "modelo",
            "valor",
            "ano",
            "quilometragem",
            "cor",
            "combustivel",
            "cambio",
            "descricao",
            "publicado",
            "destaque",
            "vendido",
        )
        widgets = {
            "modelo": forms.TextInput(attrs={"placeholder": "Ex: 911"}),
            "valor": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "ano": forms.NumberInput(attrs={"min": "1900"}),
            "quilometragem": forms.NumberInput(attrs={"min": "0"}),
            "cor": forms.TextInput(attrs={"placeholder": "Ex: Preto"}),
            "combustivel": forms.TextInput(attrs={"placeholder": "Ex: Gasolina"}),
            "cambio": forms.TextInput(attrs={"placeholder": "Ex: Automático"}),
            "descricao": forms.TextInput(attrs={"placeholder": "Ex: 2.0 Turbo"}),
        }
