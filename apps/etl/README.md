# Olho Público — ETL

Pipelines de ingestão das fontes oficiais brasileiras.

## Setup local

```bash
cd apps/etl
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

## Rodar testes

```bash
pytest -v
```

## Estrutura

- `olho_publico_etl/models/` — Pydantic models por entidade
- `olho_publico_etl/sources/` — Conectores por fonte (Portal da Transparência, Receita, CEIS, TSE, Compras, IBGE, Prefeituras)
- `olho_publico_etl/pipeline/` — Bronze (Parquet R2) → Gold (Postgres) loaders
- `olho_publico_etl/alerts/` — Engine de detecção de alertas
- `olho_publico_etl/utils/` — Helpers (mascaramento de CPF, slugify, etc.)

## Próximas fases

- **P2** — Implementar ingestão Portal da Transparência (exige chave API CGU)
- **P3** — Receita Federal CNPJ (45 GB compactado)
- **P4** — CEIS/CNEP, TSE, Compras.gov
- **P6** — Engine de alertas completo (regras restantes)
- **P7** — Scrapers de prefeituras por ERP
