# B06: busca sem acentos. Cria o campo e preenche para os produtos já existentes.
import unicodedata

from django.db import migrations, models


def _normalizar(texto):
    sem_acentos = "".join(c for c in unicodedata.normalize("NFKD", texto or "") if not unicodedata.combining(c))
    return " ".join(sem_acentos.casefold().split())


def preencher_texto_busca(apps, schema_editor):
    Produto = apps.get_model("catalogo", "Produto")
    for p in Produto.objects.select_related("categoria"):
        p.texto_busca = _normalizar(" ".join([p.nome, p.descricao, p.ingredientes, p.categoria.nome]))
        p.save(update_fields=["texto_busca"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="texto_busca",
            field=models.TextField(
                blank=True,
                editable=False,
                help_text="Nome, descrição, ingredientes e categoria normalizados (sem acentos).",
            ),
        ),
        migrations.RunPython(preencher_texto_busca, migrations.RunPython.noop),
    ]
