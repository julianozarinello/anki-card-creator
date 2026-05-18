"""Gerador de cartas Anki (.apkg) a partir de um CSV fixo na pasta do programa.

Uso:
    python criar_baralho.py

O programa lê automaticamente o arquivo 'vocabulario.csv' localizado
na mesma pasta do script.

Colunas esperadas no CSV: id, frente, verso
"""

import csv
import sys
import pathlib

import genanki

# ---------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DOS PILARES DO ANKI (IDs fixos — não altere após criar o baralho)
# ---------------------------------------------------------------------------
MODEL_ID    = 1_607_392_319          # ID único do modelo/design do cartão
DECK_ID     = 1_413_744_730          # ID único do baralho
DECK_NAME   = "Italiano :: Vocabulário"  # nome exibido no Anki
OUTPUT_FILE = "italiano.apkg"            # arquivo de saída

# Caminho fixo para o CSV — mesma pasta do script
CSV_FILE = pathlib.Path(__file__).parent / "vocabulario.csv"

# ---------------------------------------------------------------------------
# 2. MODELO VISUAL (template HTML/CSS)
# ---------------------------------------------------------------------------
CSS = """
.card {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 26px;
    text-align: center;
    color: #2c2c2c;
    background-color: #fafafa;
    padding: 40px 20px;
    line-height: 1.5;
}
.frente {
    font-weight: 700;
    font-size: 32px;
    color: #1a6b3c;
    margin-bottom: 10px;
}
.verso {
    font-size: 22px;
    color: #555;
    margin-top: 12px;
}
"""

FRONT_TEMPLATE = """
<div class="card">
    <div class="frente">{{Frente}}</div>
</div>
"""

BACK_TEMPLATE = """
{{FrontSide}}
<hr>
<div class="card">
    <div class="verso">{{Verso}}</div>
</div>
"""

# ---------------------------------------------------------------------------
# 3. LEITURA DO CSV
# ---------------------------------------------------------------------------

def ler_csv() -> list[dict]:
    """Lê o vocabulário do arquivo vocabulario.csv na pasta do programa."""
    if not CSV_FILE.exists():
        sys.exit(
            f"❌  Arquivo não encontrado: '{CSV_FILE}'\n"
            f"    Certifique-se de que 'vocabulario.csv' está na mesma pasta do script."
        )

    dados = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for linha in reader:
            dados.append({
                "id":     int(linha["id"]),
                "frente": linha["frente"].strip(),
                "verso":  linha["verso"].strip(),
            })

    if not dados:
        sys.exit("❌  O arquivo CSV está vazio ou sem linhas válidas.")

    return dados


# ---------------------------------------------------------------------------
# 4. CRIAÇÃO DO MODELO E DO BARALHO
# ---------------------------------------------------------------------------

def criar_modelo() -> genanki.Model:
    return genanki.Model(
        MODEL_ID,
        "Modelo Italiano",
        fields=[
            {"name": "Frente"},
            {"name": "Verso"},
        ],
        templates=[
            {
                "name": "Carta",
                "qfmt": FRONT_TEMPLATE,
                "afmt": BACK_TEMPLATE,
            },
        ],
        css=CSS,
    )


def criar_baralho(dados: list[dict]) -> genanki.Deck:
    modelo  = criar_modelo()
    baralho = genanki.Deck(DECK_ID, DECK_NAME)

    for item in dados:
        # GUID estático gerado a partir do ID fixo da linha
        # Garante atualização em vez de duplicata a cada reimportação
        guid = genanki.guid_for(item["id"])

        nota = genanki.Note(
            model=modelo,
            fields=[item["frente"], item["verso"]],
            guid=guid,
        )
        baralho.add_note(nota)

    return baralho


# ---------------------------------------------------------------------------
# 5. EXPORTAÇÃO
# ---------------------------------------------------------------------------

def exportar(baralho: genanki.Deck) -> None:
    saida = pathlib.Path(__file__).parent / OUTPUT_FILE
    pacote = genanki.Package(baralho)
    pacote.write_to_file(str(saida))
    print(f"✅  Baralho exportado: '{saida}'")
    print(f"    Total de cartas: {len(baralho.notes)}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dados   = ler_csv()
    baralho = criar_baralho(dados)
    exportar(baralho)
