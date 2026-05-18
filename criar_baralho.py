"""Gerador de cartas Anki (.apkg) a partir de CSV ou Excel.

Uso:
    python criar_baralho.py                     # usa dados de exemplo embutidos
    python criar_baralho.py vocabulario.csv     # lê de um CSV
    python criar_baralho.py vocabulario.xlsx    # lê de um Excel

Colunas esperadas no arquivo: id, frente, verso
"""

import sys
import csv
import pathlib

import genanki

# ---------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DOS PILARES DO ANKI (IDs fixos — não altere após criar o baralho)
# ---------------------------------------------------------------------------
MODEL_ID  = 1_607_392_319   # ID único do modelo/design do cartão
DECK_ID   = 1_413_744_730   # ID único do baralho
DECK_NAME = "Italiano :: Vocabulário"  # nome exibido no Anki
OUTPUT_FILE = "italiano.apkg"          # arquivo gerado

# ---------------------------------------------------------------------------
# 2. DADOS DE EXEMPLO (usados quando nenhum arquivo é fornecido)
# ---------------------------------------------------------------------------
DADOS_EXEMPLO = [
    {"id": 1, "frente": "Buongiorno", "verso": "Bom dia"},
    {"id": 2, "frente": "Grazie",     "verso": "Obrigado/a"},
    {"id": 3, "frente": "Prego",      "verso": "De nada / Por favor"},
    {"id": 4, "frente": "Mi chiamo…", "verso": "Meu nome é…"},
    {"id": 5, "frente": "Arrivederci","verso": "Até logo (formal)"},
]

# ---------------------------------------------------------------------------
# 3. MODELO VISUAL (template HTML/CSS)
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
    color: #1a6b3c;   /* verde para italiano */
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
# 4. FUNÇÕES DE LEITURA DE DADOS
# ---------------------------------------------------------------------------

def ler_csv(caminho: str) -> list[dict]:
    """Lê vocabulário de um arquivo CSV com colunas: id, frente, verso."""
    dados = []
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for linha in reader:
            dados.append({
                "id":     int(linha["id"]),
                "frente": linha["frente"].strip(),
                "verso":  linha["verso"].strip(),
            })
    return dados


def ler_excel(caminho: str) -> list[dict]:
    """Lê vocabulário de um arquivo Excel (.xlsx) com colunas: id, frente, verso."""
    try:
        import openpyxl
    except ImportError:
        sys.exit("Instale openpyxl para ler Excel:  pip install openpyxl")

    wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    ws = wb.active
    cabecalhos = [str(c.value).strip().lower() for c in next(ws.iter_rows(max_row=1))]
    dados = []
    for linha in ws.iter_rows(min_row=2, values_only=True):
        registro = dict(zip(cabecalhos, linha))
        if registro.get("id") is None:
            continue
        dados.append({
            "id":     int(registro["id"]),
            "frente": str(registro["frente"]).strip(),
            "verso":  str(registro["verso"]).strip(),
        })
    return dados


def carregar_dados(args: list[str]) -> list[dict]:
    """Decide a fonte de dados com base nos argumentos da linha de comando."""
    if len(args) < 2:
        print("Nenhum arquivo fornecido — usando dados de exemplo embutidos.")
        return DADOS_EXEMPLO

    caminho = pathlib.Path(args[1])
    sufixo  = caminho.suffix.lower()

    if not caminho.exists():
        sys.exit(f"Arquivo não encontrado: {caminho}")

    if sufixo == ".csv":
        return ler_csv(str(caminho))
    elif sufixo in (".xlsx", ".xls"):
        return ler_excel(str(caminho))
    else:
        sys.exit(f"Formato não suportado: '{sufixo}'. Use .csv ou .xlsx")


# ---------------------------------------------------------------------------
# 5. CRIAÇÃO DO MODELO E DO BARALHO
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
                "qfmt":  FRONT_TEMPLATE,
                "afmt":  BACK_TEMPLATE,
            },
        ],
        css=CSS,
    )


def criar_baralho(dados: list[dict]) -> genanki.Deck:
    modelo = criar_modelo()
    baralho = genanki.Deck(DECK_ID, DECK_NAME)

    for item in dados:
        # GUID estático gerado a partir do ID único da linha
        guid = genanki.guid_for(item["id"])

        nota = genanki.Note(
            model=modelo,
            fields=[item["frente"], item["verso"]],
            guid=guid,
        )
        baralho.add_note(nota)

    return baralho


# ---------------------------------------------------------------------------
# 6. EMPACOTAMENTO E EXPORTAÇÃO
# ---------------------------------------------------------------------------

def exportar(baralho: genanki.Deck, saida: str) -> None:
    pacote = genanki.Package(baralho)
    pacote.write_to_file(saida)
    print(f"✅  Baralho exportado com sucesso: '{saida}'")
    print(f"    Total de cartas: {len(baralho.notes)}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dados   = carregar_dados(sys.argv)
    baralho = criar_baralho(dados)
    exportar(baralho, OUTPUT_FILE)
