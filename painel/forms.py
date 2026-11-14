from django import forms

from catalogo.models import Categoria, Produto
from pedidos.models import ZonaEntrega


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "categoria", "descricao", "ingredientes", "preco", "estoque", "imagem", "destaque", "ativo"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 3}), "preco": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"})}


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "ordem", "ativa"]


class ZonaEntregaForm(forms.ModelForm):
    class Meta:
        model = ZonaEntrega
        fields = ["bairro", "taxa", "ativa"]
        widgets = {"taxa": forms.NumberInput(attrs={"step": "0.50", "min": "0"})}

    def clean_taxa(self):
        taxa = self.cleaned_data["taxa"]
        if taxa < 0:
            raise forms.ValidationError("A taxa não pode ser negativa.")
        return taxa
