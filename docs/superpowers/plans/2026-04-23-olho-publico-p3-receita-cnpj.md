# Olho Público — Plano P3: Ingestão Receita Federal CNPJ

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) ou superpowers:executing-plans para implementar este plano task-by-task. Steps usam checkbox (`- [ ]`).

**Goal:** Baixar e processar a base CNPJ completa da Receita Federal (~45 GB compactados) e enriquecer a tabela `empresas` com razão social real, situação cadastral, sócios, CNAE — habilitando detecção `EMPRESA_FOGUETE`, `SOCIO_SANCIONADO` e cruzamento com `/contratos/cpf-cnpj` da CGU.

**Architecture:**
1. **Download mensal** dos 21 ZIPs publicados em `dados.gov.br/cnpj` para R2 (`raw/receita-cnpj/AAAAMM/*.zip`).
2. **Parse com DuckDB** lendo direto dos ZIPs no R2 (não cabe em RAM, streaming).
3. **Filtro inteligente:** mantém apenas CNPJs já mencionados em outras fontes (`empresas.cnpj` existentes) — reduz ~50M para ~800k linhas.
4. **Upsert seletivo** em `empresas` + `socios` (só os relevantes).
5. **Enrich job /contratos/cpf-cnpj:** para cada CNPJ relevante, busca contratos federais — bypass do `codigoOrgao` mandatório.

**Tech Stack:** DuckDB 1.x · httpx (download) · Polars (transforms) · psycopg (upsert) · boto3 (R2). Rodar mensalmente via cron na VPS.

**Volumes:**
- ~45 GB ZIPs no R2 → ~120 GB descompactado em Parquet (depois descartado, mantém só Parquet otimizado em R2 bronze)
- Postgres ganha ~100 MB (apenas CNPJs filtrados)
- Tempo primeira execução: ~5h. Atualizações mensais: ~2h.

---

## Estrutura de arquivos

```
apps/etl/
└── olho_publico_etl/
    ├── sources/receita/
    │   ├── __init__.py
    │   ├── downloader.py       # Modificar: implementação real
    │   ├── parser.py           # NEW: DuckDB pipeline
    │   └── enrich.py           # NEW: enriquece empresas existentes
    ├── jobs/
    │   ├── sync_receita_cnpj.py        # NEW: orquestrador mensal
    │   └── sync_contratos_por_cnpj.py  # NEW: usa /contratos/cpf-cnpj
    └── tests/unit/
        ├── test_receita_parser.py
        └── test_receita_enrich.py
```

---

## Fase 3.1 — Download (~30 min de código)

### Task 1: Receita downloader real

**Files:** `apps/etl/olho_publico_etl/sources/receita/downloader.py`

URL base atual: `https://arquivos.receitafederal.gov.br/cnpj/dados_abertos_cnpj/`

Estrutura mensal: `AAAA-MM/Empresas{0-9}.zip`, `Estabelecimentos{0-9}.zip`, `Socios{0-9}.zip`, etc.

Implementar:
- `list_mes_disponiveis()` — lista pastas `AAAA-MM/`
- `list_arquivos(ano_mes)` — todos os ZIPs do mês
- `download_zip(url, destino_local)` — streaming
- `upload_para_r2(arquivo_local, key_r2)` — usa `make_r2_client`

Idempotente: `if r2_object_exists(key) and force=False: skip`.

### Task 2: Test downloader

Mock httpx + boto3 com respx + moto. Verifica:
- Lista de arquivos correta para um mês
- Download streaming não carrega tudo em RAM
- Skip quando arquivo já existe no R2

---

## Fase 3.2 — Parser DuckDB (~2h)

### Task 3: Parser CNPJ com DuckDB

**Files:** `apps/etl/olho_publico_etl/sources/receita/parser.py`

Schema da Receita (10 tabelas principais):
- `EMPRECSV`: empresas (CNPJ base, razão social, capital social, porte, etc.)
- `ESTABELE`: estabelecimentos (CNPJ completo + endereço + CNAE)
- `SOCIOCSV`: sócios (CPF/CNPJ + nome + qualificação)
- `SIMPLES`: opção pelo Simples Nacional
- `MOTICSV`, `MUNICCSV`, `NATJUCSV`, `PAISCSV`, `QUALSCSV`, `CNAECSV`: lookups

Pipeline DuckDB:
```sql
-- 1) Carrega ZIPs direto via httpfs do R2
INSTALL httpfs; LOAD httpfs;
SET s3_endpoint='ACCOUNT.r2.cloudflarestorage.com';
SET s3_access_key_id='...'; SET s3_secret_access_key='...';

-- 2) Lê CSVs dos ZIPs
CREATE TABLE empresas AS
SELECT * FROM read_csv_auto(
  's3://raw/receita-cnpj/AAAAMM/EmpresasN.zip!*.EMPRECSV',
  delim=';', header=false
);

-- 3) Filtra apenas CNPJs relevantes (já no Postgres)
COPY (
  SELECT e.* FROM empresas e
  JOIN postgres_scan('host=...', 'empresas') p ON p.cnpj LIKE e.cnpj_base || '%'
) TO 's3://bronze/receita-cnpj/AAAAMM/empresas-filtradas.parquet';
```

### Task 4: Test parser

Cria CSVs sample no `/tmp`, roda DuckDB local, verifica output Parquet correto.

---

## Fase 3.3 — Upsert e enriquecimento (~1h)

### Task 5: Upsert empresas + sócios

**Files:** `apps/etl/olho_publico_etl/sources/receita/enrich.py`

```python
def enrich_empresas_from_parquet(conn, parquet_url: str) -> int:
    """Lê Parquet e UPSERT em empresas (preserva flags existentes)."""
    sql = """
    INSERT INTO empresas (cnpj, razao_social, nome_fantasia, data_abertura,
                          situacao, cnae_principal, municipio_sede_id, atualizado_em)
    SELECT cnpj, razao_social, nome_fantasia, data_abertura,
           situacao, cnae_principal, municipio_ibge, NOW()
    FROM read_parquet(%s)
    ON CONFLICT (cnpj) DO UPDATE SET
      razao_social = EXCLUDED.razao_social,
      nome_fantasia = EXCLUDED.nome_fantasia,
      data_abertura = EXCLUDED.data_abertura,
      situacao = EXCLUDED.situacao,
      cnae_principal = EXCLUDED.cnae_principal,
      atualizado_em = NOW();
    """
    # via DuckDB postgres_extension OR via Python loop
```

### Task 6: Upsert sócios

Similar para `socios` table com CPF mascarado via `mask_cpf()`.

---

## Fase 3.4 — Cruzamento /contratos/cpf-cnpj (~30 min)

### Task 7: Job sync_contratos_por_cnpj

**Files:** `apps/etl/olho_publico_etl/jobs/sync_contratos_por_cnpj.py`

Endpoint `/api-de-dados/contratos/cpf-cnpj` aceita CNPJ direto. Para cada CNPJ relevante:

```python
async def fetch_contratos_da_empresa(client, cnpj):
    pagina = 1
    while True:
        params = {"cpfCnpj": cnpj, "pagina": pagina}
        data = await client.get("/api-de-dados/contratos/cpf-cnpj", params=params)
        if not data: return
        for item in data: yield parse(item)
        pagina += 1
```

Job batch: pega top 1000 CNPJs por valor já em `contratos`, busca contratos federais, popula com prefixo `[CONTRATO-FEDERAL]`.

---

## Fase 3.5 — Orquestração e schedule

### Task 8: Job principal sync_receita_cnpj

```python
def sync_receita_cnpj_mensal(settings: Settings):
    ano_mes = ano_mes_anterior()  # Receita publica com 1 mês de delay
    download_zips(ano_mes)        # Para R2 raw
    parse_para_parquet(ano_mes)   # Para R2 bronze
    enrich_empresas(ano_mes)       # Postgres
    enrich_socios(ano_mes)
```

### Task 9: Adicionar ao __main__

Agendar para rodar mensalmente (1× por mês). Cron interno: `if hoje.day == 5 and hora == 03h: sync_receita_cnpj_mensal()`.

---

## Critérios de aceite P3

- [ ] CNPJ Receita baixado e processado mensalmente, idempotente
- [ ] `empresas` enriquecida: razão social real, situação, data_abertura, sócios
- [ ] `socios` populado para os ~800k CNPJs relevantes
- [ ] Detecção `EMPRESA_FOGUETE` funciona (data_abertura < 12 meses + contrato > 500k)
- [ ] Detecção `SOCIO_SANCIONADO` funciona (sócio ∈ CEIS/CNEP)
- [ ] /contratos/cpf-cnpj traz contratos adicionais (bypass codigoOrgao)
- [ ] Disco VPS continua < 70% após primeira ingestão (Parquet em R2, não Postgres)
- [ ] Tempo primeira execução documentado (~5h estimado)
- [ ] Testes unitários para parser e enrich
- [ ] Documentação em METODOLOGIA.md sobre fonte Receita

## Observações operacionais

- **Disco temporário:** parser DuckDB precisa de ~50 GB livres no `/tmp` durante processamento. VPS tem 80 GB com 27 GB usados → folga apertada. Configurar `DUCKDB_TEMP_DIR` para volume grande ou usar streaming.
- **R2 storage:** raw + bronze ficam em ~70 GB no R2 = ~$1/mês.
- **Frequência:** mensal é suficiente. Atualizações diárias seriam waste.
- **Backfill:** primeira execução pega o último mês disponível. Histórico (anos anteriores) não é necessário pra V1.
