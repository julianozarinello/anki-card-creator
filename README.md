# 🃏 Anki Card Creator

Gerador de cartas Anki (`.apkg`) em Python usando a biblioteca [`genanki`](https://github.com/kerrickstaley/genanki).  
Suporta leitura de vocabulário via **CSV**, **Excel (.xlsx)** ou **dados embutidos no código**.

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Uso

### Opção 1 — Dados de exemplo embutidos
```bash
python criar_baralho.py
```

### Opção 2 — A partir de um CSV
```bash
python criar_baralho.py vocabulario_exemplo.csv
```

### Opção 3 — A partir de um Excel
```bash
python criar_baralho.py meu_vocabulario.xlsx
```

O arquivo **`italiano.apkg`** será criado na pasta atual.  
Importe-o no Anki via **Arquivo → Importar**.

---

## Estrutura do arquivo de entrada

O CSV ou Excel deve ter as seguintes colunas (com cabeçalho):

| id | frente | verso |
|----|--------|-------|
| 1  | Buongiorno | Bom dia |
| 2  | Grazie | Obrigado/a |

- **`id`** — número único e fixo por carta (garante atualização sem duplicatas no Anki)
- **`frente`** — frase/palavra em italiano
- **`verso`** — tradução e notas

---

## Como personalizar

| O que mudar | Onde no código |
|---|---|
| Nome do baralho | Constante `DECK_NAME` |
| Arquivo de saída | Constante `OUTPUT_FILE` |
| Cores e fontes | Variável `CSS` |
| IDs fixos (após criar o baralho, não altere!) | `MODEL_ID` e `DECK_ID` |

> ⚠️ **Importante**: os valores de `MODEL_ID` e `DECK_ID` devem permanecer os mesmos após a primeira importação.  
> Alterá-los faz o Anki criar um novo baralho em vez de atualizar o existente.

---

## Fluxo do programa

```
Arquivo CSV/Excel
       │
       ▼
  Leitura dos dados  ──► lista de dicionários {id, frente, verso}
       │
       ▼
  Loop de processamento
   ├─ GUID estático (gerado a partir do id)
   ├─ Monta objeto Note
   └─ Adiciona ao Deck
       │
       ▼
  Package.write_to_file()  ──►  italiano.apkg
```

---

## Dependências

- [`genanki`](https://github.com/kerrickstaley/genanki) — criação de arquivos `.apkg`
- [`openpyxl`](https://openpyxl.readthedocs.io/) — leitura de arquivos Excel (opcional)
