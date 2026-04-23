# Olho Público — Plano P2: Ingestão Portal da Transparência

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conectar o ETL ao Portal da Transparência da CGU, popular `municipios` (IBGE) e `contratos` (transferências federais) no Postgres, e substituir os mocks da página de cidade por dados reais, validado end-to-end com São Paulo.

**Architecture:** Cliente HTTP resiliente (auth via header `chave-api-dados`, retry exponencial em 429/5xx, rate-limit local de 90 req/min). Pipeline medallion: `raw/` (JSON original no R2) → `bronze/` (Parquet tipado no R2) → `gold/` (Postgres com `municipios`, `contratos`, `empresas`, `agregacoes_municipio`). Jobs agendados pelo `__main__` do ETL (loop horário no MVP; Dagster entra depois).

**Tech Stack:** Python 3.12 · httpx (HTTP) · tenacity (retry) · pydantic (validação) · psycopg (Postgres) · polars (Parquet) · boto3 (R2/S3) · structlog (logs) · pytest + respx (mocks HTTP) + pytest-asyncio

---

## Estrutura de arquivos (novos e modificados)

```
apps/etl/
├── olho_publico_etl/
│   ├── config.py                              # modificar: validação fail-fast
│   ├── __main__.py                            # modificar: loop agendando jobs reais
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py                      # novo: pool psycopg
│   ├── storage/
│   │   ├── __init__.py
│   │   └── r2.py                              # novo: cliente S3/R2
│   ├── sources/
│   │   ├── ibge/
│   │   │   ├── __init__.py
│   │   │   └── municipios.py                  # novo: download e parse IBGE
│   │   └── transparencia/
│   │       ├── __init__.py
│   │       ├── client.py                      # modificar: cliente real
│   │       ├── rate_limit.py                  # novo: token bucket
│   │       └── transferencias.py              # novo: endpoint transferências
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── bronze.py                          # novo: writer Parquet
│   │   └── gold.py                            # novo: upserts Postgres
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── sync_ibge.py                       # novo: job IBGE → municipios
│   │   ├── sync_transferencias.py            # novo: job Transparencia → contratos
│   │   └── recompute_agregacoes.py           # novo: recomputa agregacoes_municipio
├── tests/
│   ├── fixtures/
│   │   ├── ibge_municipios_sample.json        # novo
│   │   └── transparencia_transferencias.json  # novo
│   └── unit/
│       ├── test_transparencia_client.py       # novo
│       ├── test_transparencia_transferencias.py  # novo
│       ├── test_rate_limit.py                 # novo
│       ├── test_ibge_municipios.py            # novo
│       ├── test_gold_upsert.py                # novo
│       └── test_aggregations.py               # novo
apps/web/
├── lib/queries/municipios.ts                  # modificar: server-side DB read com fallback
├── app/(public)/cidade/[uf]/[slug]/page.tsx   # modificar: usar queries reais
└── lib/db.ts                                   # já existe — sem mudança
infra/
└── docker-compose.prod.yml                    # modificar: env vars LISTA_MUNICIPIOS_IBGE
packages/db/migrations/                         # sem mudança (migration já aplicada)
docs/
└── superpowers/plans/2026-04-23-olho-publico-p2-transparencia.md   # este arquivo
```

---

## Fase 2.1 — Fundação: config, DB, R2

### Task 1: Validação de config com fail-fast

**Files:**
- Modify: `apps/etl/olho_publico_etl/config.py`
- Test: `apps/etl/tests/unit/test_config.py`

- [ ] **Step 1: Escrever teste que verifica fail-fast**

`apps/etl/tests/unit/test_config.py`:

```python
import os
from unittest.mock import patch

import pytest

from olho_publico_etl.config import Settings, get_settings, require_settings


def test_settings_defaults_ok():
    s = Settings()
    assert s.database_url.startswith("postgresql://")


def test_require_settings_passes_with_all_set():
    with patch.dict(os.environ, {
        "TRANSPARENCIA_API_KEY": "abc",
        "R2_ACCOUNT_ID": "acc",
        "R2_ACCESS_KEY_ID": "key",
        "R2_SECRET_ACCESS_KEY": "sec",
    }, clear=False):
        get_settings.cache_clear()
        require_settings("transparencia_api_key", "r2_account_id")  # não levanta


def test_require_settings_raises_when_missing():
    get_settings.cache_clear()
    with patch.dict(os.environ, {"TRANSPARENCIA_API_KEY": ""}, clear=False):
        get_settings.cache_clear()
        with pytest.raises(RuntimeError, match="transparencia_api_key"):
            require_settings("transparencia_api_key")
```

- [ ] **Step 2: Rodar — espera falhar por `require_settings` não existir**

```bash
cd apps/etl && pytest tests/unit/test_config.py -v
# Expected: ImportError: cannot import name 'require_settings'
```

- [ ] **Step 3: Adicionar `require_settings` ao `config.py`**

`apps/etl/olho_publico_etl/config.py` (substituir o arquivo):

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/olho_publico"

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_raw: str = "olho-publico-raw"
    r2_bucket_bronze: str = "olho-publico-bronze"
    r2_bucket_backups: str = "olho-publico-backups"

    transparencia_api_key: str = ""

    # Lista CSV de IDs IBGE para sync periódico (ex: "3550308,3304557")
    ibge_sync_list: str = "3550308"

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def require_settings(*fields: str) -> None:
    """Raise RuntimeError se qualquer campo listado estiver vazio."""
    s = get_settings()
    missing = [f for f in fields if not getattr(s, f, None)]
    if missing:
        raise RuntimeError(
            f"Variáveis de ambiente obrigatórias ausentes: {', '.join(missing)}"
        )
```

- [ ] **Step 4: Rodar teste**

```bash
pytest tests/unit/test_config.py -v
# Expected: 3 passed
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/olho_publico_etl/config.py apps/etl/tests/unit/test_config.py
git commit -m "feat(etl): require_settings para validação fail-fast de envs"
```

---

### Task 2: Pool de conexão Postgres

**Files:**
- Create: `apps/etl/olho_publico_etl/db/__init__.py`
- Create: `apps/etl/olho_publico_etl/db/connection.py`
- Test: `apps/etl/tests/unit/test_db_connection.py`

- [ ] **Step 1: Teste da factory (sem conexão real)**

`apps/etl/tests/unit/test_db_connection.py`:

```python
from unittest.mock import patch

from olho_publico_etl.db.connection import make_pool


def test_make_pool_returns_connection_pool():
    with patch("olho_publico_etl.db.connection.ConnectionPool") as pool_cls:
        make_pool("postgresql://x@y/z")
        pool_cls.assert_called_once()
        conninfo = pool_cls.call_args.kwargs["conninfo"]
        assert conninfo == "postgresql://x@y/z"


def test_make_pool_min_max_sensible_defaults():
    with patch("olho_publico_etl.db.connection.ConnectionPool") as pool_cls:
        make_pool("postgresql://x@y/z")
        kwargs = pool_cls.call_args.kwargs
        assert kwargs["min_size"] == 1
        assert kwargs["max_size"] == 5
```

- [ ] **Step 2: Rodar — falha por arquivo não existir**

```bash
pytest tests/unit/test_db_connection.py -v
```

- [ ] **Step 3: Criar `db/__init__.py`**

```python
from .connection import make_pool

__all__ = ["make_pool"]
```

- [ ] **Step 4: Criar `db/connection.py`**

```python
from __future__ import annotations

from psycopg_pool import ConnectionPool


def make_pool(conninfo: str, *, min_size: int = 1, max_size: int = 5) -> ConnectionPool:
    """Cria pool de conexões Postgres reutilizável.

    min_size=1 evita lazy-connect na primeira query.
    max_size=5 é suficiente para ETL single-threaded (ingestão sequencial).
    """
    return ConnectionPool(
        conninfo=conninfo,
        min_size=min_size,
        max_size=max_size,
        open=True,
    )
```

- [ ] **Step 5: Rodar**

```bash
pytest tests/unit/test_db_connection.py -v
# Expected: 2 passed
```

- [ ] **Step 6: Commit**

```bash
git add apps/etl/olho_publico_etl/db/ apps/etl/tests/unit/test_db_connection.py
git commit -m "feat(etl): pool psycopg reutilizável em olho_publico_etl.db"
```

---

### Task 3: Cliente R2 (S3-compatible)

**Files:**
- Create: `apps/etl/olho_publico_etl/storage/__init__.py`
- Create: `apps/etl/olho_publico_etl/storage/r2.py`
- Test: `apps/etl/tests/unit/test_r2_client.py`

- [ ] **Step 1: Teste factory + endpoint correto**

`apps/etl/tests/unit/test_r2_client.py`:

```python
from unittest.mock import patch

from olho_publico_etl.storage.r2 import make_r2_client, r2_endpoint_url


def test_r2_endpoint_url_builds_correct_host():
    assert r2_endpoint_url("abc123") == "https://abc123.r2.cloudflarestorage.com"


def test_make_r2_client_configures_boto3():
    with patch("olho_publico_etl.storage.r2.boto3") as boto3:
        make_r2_client("acc", "key", "sec")
        boto3.client.assert_called_once()
        kwargs = boto3.client.call_args.kwargs
        assert kwargs["service_name"] == "s3"
        assert kwargs["endpoint_url"] == "https://acc.r2.cloudflarestorage.com"
        assert kwargs["aws_access_key_id"] == "key"
        assert kwargs["aws_secret_access_key"] == "sec"
        assert kwargs["region_name"] == "auto"
```

- [ ] **Step 2: Rodar — falha**

```bash
pytest tests/unit/test_r2_client.py -v
```

- [ ] **Step 3: Criar `storage/__init__.py`**

```python
from .r2 import R2Client, make_r2_client, r2_endpoint_url

__all__ = ["R2Client", "make_r2_client", "r2_endpoint_url"]
```

- [ ] **Step 4: Criar `storage/r2.py`**

```python
from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

import boto3

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client  # só para typecheck

R2Client = "S3Client"  # alias legível em runtime


def r2_endpoint_url(account_id: str) -> str:
    return f"https://{account_id}.r2.cloudflarestorage.com"


def make_r2_client(account_id: str, access_key: str, secret_key: str):
    return boto3.client(
        service_name="s3",
        endpoint_url=r2_endpoint_url(account_id),
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def upload_bytes(client, bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
    client.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)


def upload_fileobj(client, bucket: str, key: str, fileobj: BinaryIO) -> None:
    client.upload_fileobj(Fileobj=fileobj, Bucket=bucket, Key=key)


def download_bytes(client, bucket: str, key: str) -> bytes:
    resp = client.get_object(Bucket=bucket, Key=key)
    return resp["Body"].read()
```

- [ ] **Step 5: Rodar**

```bash
pytest tests/unit/test_r2_client.py -v
# Expected: 2 passed
```

- [ ] **Step 6: Commit**

```bash
git add apps/etl/olho_publico_etl/storage/ apps/etl/tests/unit/test_r2_client.py
git commit -m "feat(etl): cliente R2 via boto3 com endpoint Cloudflare"
```

---

## Fase 2.2 — Rate limit e cliente HTTP

### Task 4: Token bucket rate limiter

**Files:**
- Create: `apps/etl/olho_publico_etl/sources/transparencia/rate_limit.py`
- Test: `apps/etl/tests/unit/test_rate_limit.py`

- [ ] **Step 1: Teste comportamento do token bucket**

`apps/etl/tests/unit/test_rate_limit.py`:

```python
import time

from olho_publico_etl.sources.transparencia.rate_limit import TokenBucket


def test_bucket_permite_burst_inicial():
    bucket = TokenBucket(rate_per_minute=60, capacity=60)
    for _ in range(10):
        assert bucket.try_acquire() is True


def test_bucket_bloqueia_quando_vazio():
    bucket = TokenBucket(rate_per_minute=60, capacity=2)
    bucket.try_acquire()
    bucket.try_acquire()
    assert bucket.try_acquire() is False


def test_bucket_reenche_com_o_tempo():
    bucket = TokenBucket(rate_per_minute=6000, capacity=1)  # 100/s
    bucket.try_acquire()
    assert bucket.try_acquire() is False
    time.sleep(0.02)  # 20ms = ~2 tokens
    assert bucket.try_acquire() is True


def test_bucket_acquire_bloqueante_espera():
    bucket = TokenBucket(rate_per_minute=6000, capacity=1)
    bucket.try_acquire()
    t0 = time.monotonic()
    bucket.acquire()  # bloqueia ~10ms (1 token em 100/s)
    elapsed = time.monotonic() - t0
    assert 0.005 < elapsed < 0.1
```

- [ ] **Step 2: Rodar — falha**

```bash
pytest tests/unit/test_rate_limit.py -v
```

- [ ] **Step 3: Implementar `rate_limit.py`**

```python
from __future__ import annotations

import threading
import time


class TokenBucket:
    """Token bucket simples, thread-safe.

    Usado para respeitar os 90 req/min do Portal da Transparência.
    """

    def __init__(self, *, rate_per_minute: float, capacity: int | None = None):
        self.rate_per_second = rate_per_minute / 60.0
        self.capacity = capacity if capacity is not None else max(1, int(rate_per_minute))
        self._tokens = float(self.capacity)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate_per_second)
        self._last_refill = now

    def try_acquire(self, n: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= n:
                self._tokens -= n
                return True
            return False

    def acquire(self, n: int = 1) -> None:
        """Bloqueia até ter tokens suficientes."""
        while True:
            if self.try_acquire(n):
                return
            # Calcula quanto tempo falta para ter `n` tokens
            with self._lock:
                deficit = n - self._tokens
                wait = deficit / self.rate_per_second
            time.sleep(max(0.001, wait))
```

- [ ] **Step 4: Rodar**

```bash
pytest tests/unit/test_rate_limit.py -v
# Expected: 4 passed
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/olho_publico_etl/sources/transparencia/rate_limit.py apps/etl/tests/unit/test_rate_limit.py
git commit -m "feat(etl): token bucket rate limiter thread-safe"
```

---

### Task 5: Cliente HTTP Portal da Transparência

**Files:**
- Modify: `apps/etl/olho_publico_etl/sources/transparencia/client.py`
- Create: `apps/etl/tests/fixtures/transparencia_transferencias.json`
- Create: `apps/etl/tests/unit/test_transparencia_client.py`

- [ ] **Step 1: Fixture de resposta da API**

`apps/etl/tests/fixtures/transparencia_transferencias.json`:

```json
[
  {
    "id": 123456,
    "mesAno": "2025-01",
    "valor": 1234567.89,
    "favorecido": {
      "nome": "PREFEITURA MUNICIPAL DE SAO PAULO",
      "codigoFormatado": "12.345.678/0001-90"
    },
    "municipio": {
      "codigoIBGE": "3550308",
      "nomeIBGE": "São Paulo",
      "uf": {"sigla": "SP"}
    },
    "programa": {"codigo": "0089", "descricao": "Assistência Farmacêutica"},
    "acaoOrcamentaria": {"descricao": "Transferência SUS"},
    "linguagemCidada": "Repasse federal para saúde básica"
  },
  {
    "id": 123457,
    "mesAno": "2025-01",
    "valor": 500000.00,
    "favorecido": {
      "nome": "PREFEITURA MUNICIPAL DE SAO PAULO",
      "codigoFormatado": "12.345.678/0001-90"
    },
    "municipio": {
      "codigoIBGE": "3550308",
      "nomeIBGE": "São Paulo",
      "uf": {"sigla": "SP"}
    },
    "programa": {"codigo": "1234", "descricao": "FUNDEB"},
    "acaoOrcamentaria": {"descricao": "FUNDEB complementar"},
    "linguagemCidada": "Complementação federal ao FUNDEB"
  }
]
```

- [ ] **Step 2: Teste do cliente com respx (mock HTTP)**

`apps/etl/tests/unit/test_transparencia_client.py`:

```python
import json
from pathlib import Path

import httpx
import pytest
import respx

from olho_publico_etl.sources.transparencia.client import TransparenciaClient

FIXTURE = Path(__file__).parent.parent / "fixtures" / "transparencia_transferencias.json"


@pytest.mark.asyncio
async def test_client_envia_chave_api_no_header():
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        mock.get("/api-de-dados/transferencias").mock(
            return_value=httpx.Response(200, json=[])
        )
        async with TransparenciaClient(api_key="minha-chave") as c:
            await c.get("/api-de-dados/transferencias")
        req = mock.calls.last.request
        assert req.headers["chave-api-dados"] == "minha-chave"


@pytest.mark.asyncio
async def test_client_desserializa_json():
    payload = json.loads(FIXTURE.read_text())
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        mock.get("/api-de-dados/transferencias").mock(
            return_value=httpx.Response(200, json=payload)
        )
        async with TransparenciaClient(api_key="k") as c:
            data = await c.get("/api-de-dados/transferencias")
        assert len(data) == 2
        assert data[0]["municipio"]["codigoIBGE"] == "3550308"


@pytest.mark.asyncio
async def test_client_retry_em_429():
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        route = mock.get("/api-de-dados/transferencias").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "0"}),
                httpx.Response(200, json=[{"ok": True}]),
            ]
        )
        async with TransparenciaClient(api_key="k") as c:
            data = await c.get("/api-de-dados/transferencias")
        assert route.call_count == 2
        assert data == [{"ok": True}]


@pytest.mark.asyncio
async def test_client_propaga_erro_4xx_nao_transitorio():
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        mock.get("/api-de-dados/transferencias").mock(
            return_value=httpx.Response(401, json={"error": "unauthorized"})
        )
        async with TransparenciaClient(api_key="k") as c:
            with pytest.raises(httpx.HTTPStatusError):
                await c.get("/api-de-dados/transferencias")
```

- [ ] **Step 3: Rodar — falha por import ou assinatura errada**

```bash
pytest tests/unit/test_transparencia_client.py -v
```

- [ ] **Step 4: Atualizar pyproject para incluir respx**

Editar `apps/etl/pyproject.toml` — garantir que `respx>=0.21.0` está em `[project.optional-dependencies].dev`. Se já estiver, pular.

- [ ] **Step 5: Implementar `client.py`** (substituir o skeleton atual)

`apps/etl/olho_publico_etl/sources/transparencia/client.py`:

```python
from __future__ import annotations

import asyncio
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .rate_limit import TokenBucket

BASE_URL = "https://api.portaldatransparencia.gov.br"
DEFAULT_RATE_PER_MINUTE = 90  # limite oficial CGU


class TransparenciaClient:
    """Cliente HTTP para api.portaldatransparencia.gov.br.

    - Header de auth: chave-api-dados
    - Rate limit local: 90 req/min (respeita CGU)
    - Retry exponencial em 429/5xx via tenacity
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        rate_per_minute: int = DEFAULT_RATE_PER_MINUTE,
        timeout_seconds: float = 30.0,
    ):
        if not api_key:
            raise ValueError("api_key obrigatória (variável TRANSPARENCIA_API_KEY)")
        self._bucket = TokenBucket(rate_per_minute=rate_per_minute)
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"chave-api-dados": api_key, "Accept": "application/json"},
            timeout=timeout_seconds,
        )

    async def __aenter__(self) -> "TransparenciaClient":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self._client.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, _TransientHttpError := type)),  # placeholder, ver Step 6
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        # bloqueia até ter token
        await asyncio.get_running_loop().run_in_executor(None, self._bucket.acquire)
        resp = await self._client.request(method, path, **kwargs)
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            raise httpx.HTTPStatusError(
                f"status={resp.status_code}", request=resp.request, response=resp
            )
        resp.raise_for_status()
        return resp

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        resp = await self._request("GET", path, params=params)
        return resp.json()
```

- [ ] **Step 6: Ajustar o decorator `@retry` para detectar 429/5xx correto**

Corrigir o `_request` para usar a classe correta no retry:

Substitua o decorator por:

```python
    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
```

- [ ] **Step 7: Rodar testes**

```bash
pytest tests/unit/test_transparencia_client.py -v
# Expected: 4 passed
```

- [ ] **Step 8: Commit**

```bash
git add apps/etl/olho_publico_etl/sources/transparencia/client.py \
        apps/etl/tests/unit/test_transparencia_client.py \
        apps/etl/tests/fixtures/transparencia_transferencias.json
git commit -m "feat(etl): cliente HTTP Transparencia com auth+retry+rate-limit"
```

---

## Fase 2.3 — IBGE municípios

### Task 6: Loader IBGE municipios

**Files:**
- Create: `apps/etl/olho_publico_etl/sources/ibge/municipios.py`
- Create: `apps/etl/tests/fixtures/ibge_municipios_sample.json`
- Create: `apps/etl/tests/unit/test_ibge_municipios.py`

- [ ] **Step 1: Fixture reduzida da API IBGE**

`apps/etl/tests/fixtures/ibge_municipios_sample.json`:

```json
[
  {
    "id": 3550308,
    "nome": "São Paulo",
    "microrregiao": {
      "mesorregiao": {
        "UF": {"id": 35, "sigla": "SP", "nome": "São Paulo"}
      }
    }
  },
  {
    "id": 2611606,
    "nome": "Recife",
    "microrregiao": {
      "mesorregiao": {
        "UF": {"id": 26, "sigla": "PE", "nome": "Pernambuco"}
      }
    }
  }
]
```

- [ ] **Step 2: Teste parse + slug**

`apps/etl/tests/unit/test_ibge_municipios.py`:

```python
import json
from pathlib import Path

from olho_publico_etl.sources.ibge.municipios import parse_ibge_payload

FIXTURE = Path(__file__).parent.parent / "fixtures" / "ibge_municipios_sample.json"


def test_parse_retorna_municipio_com_slug_e_uf():
    payload = json.loads(FIXTURE.read_text())
    rows = list(parse_ibge_payload(payload))
    assert len(rows) == 2
    sp = rows[0]
    assert sp.id_ibge == "3550308"
    assert sp.nome == "São Paulo"
    assert sp.uf == "SP"
    assert sp.slug == "sao-paulo"
    assert sp.cobertura_prefeitura == "nenhuma"


def test_parse_id_ibge_como_string_7_digitos():
    payload = [{"id": 123, "nome": "X", "microrregiao": {"mesorregiao": {"UF": {"sigla": "SP"}}}}]
    rows = list(parse_ibge_payload(payload))
    assert rows[0].id_ibge == "0000123"
```

- [ ] **Step 3: Rodar — falha**

```bash
pytest tests/unit/test_ibge_municipios.py -v
```

- [ ] **Step 4: Implementar `sources/ibge/municipios.py`**

`apps/etl/olho_publico_etl/sources/ibge/__init__.py`:

```python
"""IBGE — municípios, população e IDH. Implementação plena no plano P2."""

from .municipios import fetch_ibge_municipios, parse_ibge_payload

__all__ = ["fetch_ibge_municipios", "parse_ibge_payload"]
```

`apps/etl/olho_publico_etl/sources/ibge/municipios.py`:

```python
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx

from olho_publico_etl.models import Municipio
from olho_publico_etl.utils import slugify

IBGE_MUNICIPIOS_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


def fetch_ibge_municipios(timeout_seconds: float = 30.0) -> list[dict[str, Any]]:
    """Baixa a lista completa de 5.570 municípios do IBGE."""
    with httpx.Client(timeout=timeout_seconds) as c:
        resp = c.get(IBGE_MUNICIPIOS_URL)
        resp.raise_for_status()
        return resp.json()


def parse_ibge_payload(payload: list[dict[str, Any]]) -> Iterator[Municipio]:
    """Converte resposta do IBGE em Municipio (Pydantic)."""
    for m in payload:
        id_ibge = str(m["id"]).zfill(7)
        nome = m["nome"]
        uf = m["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        yield Municipio(
            id_ibge=id_ibge,
            nome=nome,
            slug=slugify(nome),
            uf=uf,
            cobertura_prefeitura="nenhuma",
        )
```

- [ ] **Step 5: Rodar**

```bash
pytest tests/unit/test_ibge_municipios.py -v
# Expected: 2 passed
```

- [ ] **Step 6: Commit**

```bash
git add apps/etl/olho_publico_etl/sources/ibge/ \
        apps/etl/tests/unit/test_ibge_municipios.py \
        apps/etl/tests/fixtures/ibge_municipios_sample.json
git commit -m "feat(etl): source IBGE com fetch e parse de municípios"
```

---

### Task 7: Fetcher de transferências federais

**Files:**
- Create: `apps/etl/olho_publico_etl/sources/transparencia/transferencias.py`
- Create: `apps/etl/tests/unit/test_transparencia_transferencias.py`

- [ ] **Step 1: Teste parse do payload**

`apps/etl/tests/unit/test_transparencia_transferencias.py`:

```python
import json
from pathlib import Path

from olho_publico_etl.sources.transparencia.transferencias import parse_transferencias_payload

FIXTURE = Path(__file__).parent.parent / "fixtures" / "transparencia_transferencias.json"


def test_parse_gera_contratos_com_fonte_e_cnpj_limpo():
    payload = json.loads(FIXTURE.read_text())
    rows = list(parse_transferencias_payload(payload))
    assert len(rows) == 2

    r = rows[0]
    assert r.fonte == "portal_transparencia"
    assert r.cnpj_fornecedor == "12345678000190"  # sem pontuação
    assert r.municipio_aplicacao_id == "3550308"
    assert r.orgao_contratante == "Governo Federal"
    assert str(r.valor) == "1234567.89"
    assert "Assistência Farmacêutica" in r.objeto


def test_parse_ignora_registros_sem_cnpj():
    bad = [{"id": 1, "mesAno": "2025-01", "valor": 100,
            "favorecido": {"nome": "X", "codigoFormatado": ""},
            "municipio": {"codigoIBGE": "3550308"},
            "programa": {"descricao": "p"}, "acaoOrcamentaria": {"descricao": "a"}}]
    assert list(parse_transferencias_payload(bad)) == []
```

- [ ] **Step 2: Rodar — falha**

```bash
pytest tests/unit/test_transparencia_transferencias.py -v
```

- [ ] **Step 3: Implementar `transferencias.py`**

`apps/etl/olho_publico_etl/sources/transparencia/transferencias.py`:

```python
from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/transferencias"
MAX_PAGE_SIZE = 500


def _clean_cnpj(cnpj_formatted: str) -> str | None:
    digits = "".join(c for c in cnpj_formatted if c.isdigit())
    return digits if len(digits) == 14 else None


def _ano_mes_to_date(ano_mes: str) -> date:
    """'2025-01' → date(2025, 1, 1)."""
    ano, mes = ano_mes.split("-")
    return date(int(ano), int(mes), 1)


def parse_transferencias_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    """Converte resposta de /transferencias em Contrato."""
    for item in payload:
        favorecido = item.get("favorecido", {}) or {}
        cnpj = _clean_cnpj(favorecido.get("codigoFormatado", ""))
        if not cnpj:
            continue
        municipio = item.get("municipio", {}) or {}
        municipio_id = municipio.get("codigoIBGE") or None

        programa = (item.get("programa") or {}).get("descricao", "")
        acao = (item.get("acaoOrcamentaria") or {}).get("descricao", "")
        linguagem = item.get("linguagemCidada") or ""
        objeto = f"{programa} — {acao}".strip(" —") or linguagem or "Transferência federal"

        yield Contrato(
            municipio_aplicacao_id=municipio_id,
            cnpj_fornecedor=cnpj,
            orgao_contratante="Governo Federal",
            objeto=objeto,
            valor=Decimal(str(item["valor"])),
            data_assinatura=_ano_mes_to_date(item["mesAno"]),
            modalidade_licitacao=None,
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_transferencias_municipio(
    client: TransparenciaClient,
    *,
    codigo_ibge: str,
    ano_mes: str,
) -> AsyncIterator[Contrato]:
    """Pagina /transferencias para um município, mês a mês, até esgotar páginas."""
    pagina = 1
    while True:
        params = {
            "codigoIbge": codigo_ibge,
            "anoMesReferencia": ano_mes.replace("-", ""),  # API aceita YYYYMM
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for contrato in parse_transferencias_payload(data):
            yield contrato
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1
```

- [ ] **Step 4: Rodar**

```bash
pytest tests/unit/test_transparencia_transferencias.py -v
# Expected: 2 passed
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/olho_publico_etl/sources/transparencia/transferencias.py \
        apps/etl/tests/unit/test_transparencia_transferencias.py
git commit -m "feat(etl): fetcher paginado de transferencias federais"
```

---

## Fase 2.4 — Pipeline Bronze e Gold

### Task 8: Writer Parquet (Bronze R2)

**Files:**
- Create: `apps/etl/olho_publico_etl/pipeline/__init__.py`
- Create: `apps/etl/olho_publico_etl/pipeline/bronze.py`
- Test: `apps/etl/tests/unit/test_bronze_writer.py`

- [ ] **Step 1: Teste escrita Parquet in-memory**

`apps/etl/tests/unit/test_bronze_writer.py`:

```python
import io
from datetime import date
from decimal import Decimal

import polars as pl

from olho_publico_etl.models import Contrato
from olho_publico_etl.pipeline.bronze import contratos_to_parquet_bytes


def test_contratos_to_parquet_roundtrip():
    rows = [
        Contrato(
            municipio_aplicacao_id="3550308",
            cnpj_fornecedor="12345678000190",
            orgao_contratante="Governo Federal",
            objeto="Repasse SUS",
            valor=Decimal("1000.50"),
            data_assinatura=date(2025, 1, 1),
            fonte="portal_transparencia",
        )
    ]
    blob = contratos_to_parquet_bytes(rows)
    df = pl.read_parquet(io.BytesIO(blob))
    assert df.height == 1
    assert df["cnpj_fornecedor"][0] == "12345678000190"
    assert df["municipio_aplicacao_id"][0] == "3550308"
```

- [ ] **Step 2: Rodar — falha**

```bash
pytest tests/unit/test_bronze_writer.py -v
```

- [ ] **Step 3: Implementar `pipeline/bronze.py`**

`apps/etl/olho_publico_etl/pipeline/__init__.py`:

```python
"""Bronze (Parquet no R2) e Gold (Postgres) — pipeline medallion."""
```

`apps/etl/olho_publico_etl/pipeline/bronze.py`:

```python
from __future__ import annotations

import io
from collections.abc import Iterable

import polars as pl

from olho_publico_etl.models import Contrato


def contratos_to_parquet_bytes(rows: Iterable[Contrato]) -> bytes:
    """Serializa lista de Contrato em Parquet (bytes), schema plano."""
    records = [
        {
            "municipio_aplicacao_id": r.municipio_aplicacao_id,
            "cnpj_fornecedor": r.cnpj_fornecedor,
            "orgao_contratante": r.orgao_contratante,
            "objeto": r.objeto,
            "valor": str(r.valor),  # preserva precisão
            "data_assinatura": r.data_assinatura.isoformat(),
            "modalidade_licitacao": r.modalidade_licitacao,
            "fonte": r.fonte,
            "dados_originais_url": r.dados_originais_url,
        }
        for r in rows
    ]
    df = pl.DataFrame(records)
    buf = io.BytesIO()
    df.write_parquet(buf, compression="snappy")
    return buf.getvalue()


def bronze_key_transferencias(codigo_ibge: str, ano_mes: str) -> str:
    """Ex: bronze/transferencias/3550308/2025-01.parquet"""
    return f"bronze/transferencias/{codigo_ibge}/{ano_mes}.parquet"
```

- [ ] **Step 4: Rodar**

```bash
pytest tests/unit/test_bronze_writer.py -v
# Expected: 1 passed
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/olho_publico_etl/pipeline/ apps/etl/tests/unit/test_bronze_writer.py
git commit -m "feat(etl): writer Parquet para camada Bronze (R2)"
```

---

### Task 9: Gold upsert de municípios

**Files:**
- Create: `apps/etl/olho_publico_etl/pipeline/gold.py`
- Create: `apps/etl/tests/unit/test_gold_upsert.py`

- [ ] **Step 1: Teste de upsert via SQL mockado**

`apps/etl/tests/unit/test_gold_upsert.py`:

```python
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from olho_publico_etl.models import Contrato, Empresa, Municipio
from olho_publico_etl.pipeline.gold import upsert_contratos, upsert_empresas, upsert_municipios


def _fake_conn():
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchone.return_value = (0,)
    return conn, cur


def test_upsert_municipios_executa_uma_query_por_batch():
    conn, cur = _fake_conn()
    m = [Municipio(id_ibge="3550308", nome="São Paulo", slug="sao-paulo", uf="SP")]
    upsert_municipios(conn, m)
    assert cur.executemany.called
    sql = cur.executemany.call_args.args[0]
    assert "INSERT INTO municipios" in sql
    assert "ON CONFLICT" in sql


def test_upsert_empresas_minimo():
    conn, cur = _fake_conn()
    e = [Empresa(cnpj="12345678000190", razao_social="X Ltda")]
    upsert_empresas(conn, e)
    cur.executemany.assert_called_once()
    sql = cur.executemany.call_args.args[0]
    assert "INSERT INTO empresas" in sql
    assert "ON CONFLICT (cnpj) DO UPDATE" in sql


def test_upsert_contratos_insert_simples():
    conn, cur = _fake_conn()
    c = [Contrato(
        municipio_aplicacao_id="3550308",
        cnpj_fornecedor="12345678000190",
        orgao_contratante="Governo Federal",
        objeto="x",
        valor=Decimal("100"),
        data_assinatura=date(2025, 1, 1),
        fonte="portal_transparencia",
    )]
    upsert_contratos(conn, c)
    cur.executemany.assert_called_once()
    sql = cur.executemany.call_args.args[0]
    assert "INSERT INTO contratos" in sql
    # Contratos são imutáveis — não tem ON CONFLICT UPDATE (evita duplicação)
    assert "ON CONFLICT" not in sql or "DO NOTHING" in sql
```

- [ ] **Step 2: Rodar — falha**

```bash
pytest tests/unit/test_gold_upsert.py -v
```

- [ ] **Step 3: Implementar `pipeline/gold.py`**

`apps/etl/olho_publico_etl/pipeline/gold.py`:

```python
from __future__ import annotations

from collections.abc import Iterable

from olho_publico_etl.models import Contrato, Empresa, Municipio


_MUNICIPIOS_SQL = """
INSERT INTO municipios (id_ibge, nome, slug, uf, cobertura_prefeitura)
VALUES (%(id_ibge)s, %(nome)s, %(slug)s, %(uf)s, %(cobertura_prefeitura)s)
ON CONFLICT (id_ibge) DO UPDATE
SET nome = EXCLUDED.nome,
    slug = EXCLUDED.slug,
    uf = EXCLUDED.uf,
    atualizado_em = NOW();
"""


def upsert_municipios(conn, municipios: Iterable[Municipio]) -> int:
    params = [
        {
            "id_ibge": m.id_ibge,
            "nome": m.nome,
            "slug": m.slug,
            "uf": m.uf,
            "cobertura_prefeitura": m.cobertura_prefeitura,
        }
        for m in municipios
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_MUNICIPIOS_SQL, params)
    conn.commit()
    return len(params)


_EMPRESAS_SQL = """
INSERT INTO empresas (cnpj, razao_social, flags)
VALUES (%(cnpj)s, %(razao_social)s, %(flags)s::jsonb)
ON CONFLICT (cnpj) DO UPDATE
SET razao_social = COALESCE(NULLIF(EXCLUDED.razao_social, ''), empresas.razao_social),
    atualizado_em = NOW();
"""


def upsert_empresas(conn, empresas: Iterable[Empresa]) -> int:
    import json
    params = [
        {
            "cnpj": e.cnpj,
            "razao_social": e.razao_social,
            "flags": json.dumps(e.flags),
        }
        for e in empresas
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_EMPRESAS_SQL, params)
    conn.commit()
    return len(params)


_CONTRATOS_SQL = """
INSERT INTO contratos (
    municipio_aplicacao_id, cnpj_fornecedor, orgao_contratante, objeto,
    valor, data_assinatura, modalidade_licitacao, fonte, dados_originais_url
) VALUES (
    %(municipio_aplicacao_id)s, %(cnpj_fornecedor)s, %(orgao_contratante)s, %(objeto)s,
    %(valor)s, %(data_assinatura)s, %(modalidade_licitacao)s, %(fonte)s, %(dados_originais_url)s
);
"""


def upsert_contratos(conn, contratos: Iterable[Contrato]) -> int:
    params = [
        {
            "municipio_aplicacao_id": c.municipio_aplicacao_id,
            "cnpj_fornecedor": c.cnpj_fornecedor,
            "orgao_contratante": c.orgao_contratante,
            "objeto": c.objeto,
            "valor": str(c.valor),
            "data_assinatura": c.data_assinatura,
            "modalidade_licitacao": c.modalidade_licitacao,
            "fonte": c.fonte,
            "dados_originais_url": c.dados_originais_url,
        }
        for c in contratos
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_CONTRATOS_SQL, params)
    conn.commit()
    return len(params)
```

- [ ] **Step 4: Rodar**

```bash
pytest tests/unit/test_gold_upsert.py -v
# Expected: 3 passed
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/olho_publico_etl/pipeline/gold.py apps/etl/tests/unit/test_gold_upsert.py
git commit -m "feat(etl): upserts Gold (municipios, empresas, contratos)"
```

---

### Task 10: Recompute agregações por município

**Files:**
- Create: `apps/etl/olho_publico_etl/jobs/__init__.py`
- Create: `apps/etl/olho_publico_etl/jobs/recompute_agregacoes.py`
- Create: `apps/etl/tests/unit/test_aggregations.py`

- [ ] **Step 1: Teste recompute — verifica SQL contém agregações esperadas**

`apps/etl/tests/unit/test_aggregations.py`:

```python
from unittest.mock import MagicMock

from olho_publico_etl.jobs.recompute_agregacoes import recompute_agregacoes_municipio


def test_recompute_executa_sql_de_agregacao_e_upsert():
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchone.return_value = None  # agregação existente

    recompute_agregacoes_municipio(conn, municipio_id="3550308", ano=2025)

    calls = cur.execute.call_args_list
    sqls = [c.args[0] for c in calls]
    joined = " ".join(sqls)

    assert "SUM(valor)" in joined or "sum(valor)" in joined
    assert "agregacoes_municipio" in joined
    assert "municipio_aplicacao_id" in joined
```

- [ ] **Step 2: Rodar — falha**

```bash
pytest tests/unit/test_aggregations.py -v
```

- [ ] **Step 3: Implementar `jobs/recompute_agregacoes.py`**

`apps/etl/olho_publico_etl/jobs/__init__.py`:

```python
"""Jobs orquestrados pelo __main__ do ETL."""
```

`apps/etl/olho_publico_etl/jobs/recompute_agregacoes.py`:

```python
from __future__ import annotations

import json

_TOTALS_SQL = """
SELECT
    COALESCE(SUM(valor) FILTER (WHERE fonte = 'portal_transparencia'), 0) AS total_federais,
    COUNT(*)           FILTER (WHERE fonte = 'portal_transparencia')    AS qtd_federais,
    COALESCE(SUM(valor) FILTER (WHERE fonte LIKE 'prefeitura_%'), 0)    AS total_prefeitura,
    COUNT(*)           FILTER (WHERE fonte LIKE 'prefeitura_%')         AS qtd_prefeitura
FROM contratos
WHERE municipio_aplicacao_id = %s
  AND EXTRACT(YEAR FROM data_assinatura) = %s;
"""

_TOP_FORNECEDORES_SQL = """
SELECT
    c.cnpj_fornecedor,
    COALESCE(e.razao_social, '—') AS razao_social,
    COUNT(*)             AS total_contratos,
    SUM(c.valor)::text   AS valor_total
FROM contratos c
LEFT JOIN empresas e ON e.cnpj = c.cnpj_fornecedor
WHERE c.municipio_aplicacao_id = %s
  AND EXTRACT(YEAR FROM c.data_assinatura) = %s
  AND c.cnpj_fornecedor IS NOT NULL
GROUP BY c.cnpj_fornecedor, e.razao_social
ORDER BY SUM(c.valor) DESC
LIMIT 10;
"""

_UPSERT_AGREGACAO_SQL = """
INSERT INTO agregacoes_municipio (
    municipio_id, ano_referencia,
    total_contratos_federais, total_contratos_prefeitura,
    qtd_contratos_federais, qtd_contratos_prefeitura,
    top_fornecedores, gastos_por_area, comparacao_similares,
    atualizado_em
) VALUES (
    %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, NOW()
)
ON CONFLICT (municipio_id, ano_referencia) DO UPDATE
SET total_contratos_federais = EXCLUDED.total_contratos_federais,
    total_contratos_prefeitura = EXCLUDED.total_contratos_prefeitura,
    qtd_contratos_federais = EXCLUDED.qtd_contratos_federais,
    qtd_contratos_prefeitura = EXCLUDED.qtd_contratos_prefeitura,
    top_fornecedores = EXCLUDED.top_fornecedores,
    gastos_por_area = EXCLUDED.gastos_por_area,
    comparacao_similares = EXCLUDED.comparacao_similares,
    atualizado_em = NOW();
"""


def recompute_agregacoes_municipio(conn, municipio_id: str, ano: int) -> None:
    """Recomputa a linha em agregacoes_municipio para (municipio_id, ano).

    Em P2: totals + top fornecedores. Gastos_por_area e comparacao_similares
    ficam como listas vazias — entram em planos posteriores.
    """
    with conn.cursor() as cur:
        cur.execute(_TOTALS_SQL, (municipio_id, ano))
        row = cur.fetchone()
        total_fed, qtd_fed, total_pref, qtd_pref = row if row else (0, 0, 0, 0)

        cur.execute(_TOP_FORNECEDORES_SQL, (municipio_id, ano))
        top_rows = cur.fetchall()
        top = [
            {
                "cnpj": r[0],
                "razaoSocial": r[1],
                "totalContratos": int(r[2]),
                "valorTotal": str(r[3]),
            }
            for r in top_rows
        ]

        cur.execute(
            _UPSERT_AGREGACAO_SQL,
            (
                municipio_id,
                ano,
                str(total_fed),
                str(total_pref),
                int(qtd_fed),
                int(qtd_pref),
                json.dumps(top),
                json.dumps([]),
                json.dumps([]),
            ),
        )
    conn.commit()
```

- [ ] **Step 4: Rodar**

```bash
pytest tests/unit/test_aggregations.py -v
# Expected: 1 passed
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/olho_publico_etl/jobs/ apps/etl/tests/unit/test_aggregations.py
git commit -m "feat(etl): recompute agregações por município/ano"
```

---

## Fase 2.5 — Jobs orquestrados

### Task 11: Job sync IBGE

**Files:**
- Create: `apps/etl/olho_publico_etl/jobs/sync_ibge.py`

- [ ] **Step 1: Implementar job**

`apps/etl/olho_publico_etl/jobs/sync_ibge.py`:

```python
from __future__ import annotations

from olho_publico_etl.db import make_pool
from olho_publico_etl.pipeline.gold import upsert_municipios
from olho_publico_etl.sources.ibge.municipios import (
    fetch_ibge_municipios,
    parse_ibge_payload,
)


def run(database_url: str) -> int:
    """Baixa lista do IBGE e faz upsert em municipios. Retorna qtd inseridos/atualizados."""
    payload = fetch_ibge_municipios()
    municipios = list(parse_ibge_payload(payload))
    pool = make_pool(database_url)
    try:
        with pool.connection() as conn:
            return upsert_municipios(conn, municipios)
    finally:
        pool.close()
```

- [ ] **Step 2: Smoke test manual local (dev) — opcional**

```bash
cd apps/etl && python -c "
from olho_publico_etl.jobs.sync_ibge import run
print(run('postgresql://olho-publico:senha@localhost:5432/olho_publico'))
" 
# Expected: 5570
```

(Pular se não tiver Postgres local, vai rodar em produção de qualquer forma.)

- [ ] **Step 3: Commit**

```bash
git add apps/etl/olho_publico_etl/jobs/sync_ibge.py
git commit -m "feat(etl): job sync_ibge (baixa 5570 municipios e faz upsert)"
```

---

### Task 12: Job sync transferências

**Files:**
- Create: `apps/etl/olho_publico_etl/jobs/sync_transferencias.py`

- [ ] **Step 1: Implementar job**

`apps/etl/olho_publico_etl/jobs/sync_transferencias.py`:

```python
from __future__ import annotations

import asyncio
from datetime import date

from olho_publico_etl.config import Settings
from olho_publico_etl.db import make_pool
from olho_publico_etl.models import Empresa
from olho_publico_etl.pipeline.bronze import (
    bronze_key_transferencias,
    contratos_to_parquet_bytes,
)
from olho_publico_etl.pipeline.gold import upsert_contratos, upsert_empresas
from olho_publico_etl.sources.transparencia.client import TransparenciaClient
from olho_publico_etl.sources.transparencia.transferencias import (
    fetch_transferencias_municipio,
)
from olho_publico_etl.storage.r2 import make_r2_client, upload_bytes

from .recompute_agregacoes import recompute_agregacoes_municipio


async def _collect_contratos(api_key: str, codigo_ibge: str, ano_mes: str) -> list:
    async with TransparenciaClient(api_key=api_key) as c:
        out = []
        async for contrato in fetch_transferencias_municipio(
            c, codigo_ibge=codigo_ibge, ano_mes=ano_mes
        ):
            out.append(contrato)
        return out


def sync_transferencias_mes(settings: Settings, codigo_ibge: str, ano_mes: str) -> int:
    """Sincroniza um município/mês: fetch → Bronze R2 → Gold Postgres → agregações.

    Retorna a quantidade de contratos inseridos.
    """
    contratos = asyncio.run(_collect_contratos(settings.transparencia_api_key, codigo_ibge, ano_mes))
    if not contratos:
        return 0

    # Bronze (R2) — somente se R2 configurado
    if settings.r2_account_id and settings.r2_access_key_id:
        r2 = make_r2_client(
            settings.r2_account_id,
            settings.r2_access_key_id,
            settings.r2_secret_access_key,
        )
        blob = contratos_to_parquet_bytes(contratos)
        upload_bytes(
            r2,
            settings.r2_bucket_bronze,
            bronze_key_transferencias(codigo_ibge, ano_mes),
            blob,
            content_type="application/parquet",
        )

    # Gold (Postgres)
    empresas_min = [
        Empresa(cnpj=c.cnpj_fornecedor, razao_social="")  # razão vazia preserva existente
        for c in contratos
        if c.cnpj_fornecedor
    ]
    pool = make_pool(settings.database_url)
    try:
        with pool.connection() as conn:
            upsert_empresas(conn, empresas_min)
            n = upsert_contratos(conn, contratos)
            ano = int(ano_mes.split("-")[0])
            recompute_agregacoes_municipio(conn, codigo_ibge, ano)
    finally:
        pool.close()

    return n


def run_multiplas_cidades(settings: Settings, ibge_ids: list[str], ano_mes: str) -> dict[str, int]:
    """Sincroniza vários municípios sequencialmente."""
    return {
        ibge: sync_transferencias_mes(settings, ibge, ano_mes) for ibge in ibge_ids
    }
```

- [ ] **Step 2: Commit**

```bash
git add apps/etl/olho_publico_etl/jobs/sync_transferencias.py
git commit -m "feat(etl): job sync_transferencias (Bronze R2 + Gold Postgres + agregacoes)"
```

---

### Task 13: Atualizar `__main__` para executar jobs

**Files:**
- Modify: `apps/etl/olho_publico_etl/__main__.py`

- [ ] **Step 1: Substituir o heartbeat puro por loop de jobs**

`apps/etl/olho_publico_etl/__main__.py`:

```python
"""Entry point do container ETL.

Roda jobs agendados em loop simples (P2). Dagster entra depois.

Comportamento:
- Ao iniciar: sync IBGE (idempotente, rápido)
- A cada 6h: sync transferências para os IBGE_SYNC_LIST do mês atual
- Loop dorme 6h entre execuções

Em P6+ migramos para Dagster com schedules declarativos.
"""

from __future__ import annotations

import sys
import time
import traceback
from datetime import UTC, datetime

from olho_publico_etl import __version__
from olho_publico_etl.config import Settings, get_settings, require_settings
from olho_publico_etl.jobs.sync_ibge import run as run_sync_ibge
from olho_publico_etl.jobs.sync_transferencias import run_multiplas_cidades

JOB_INTERVAL_SECONDS = 6 * 3600  # 6h


def _ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(msg: str) -> None:
    print(f"[{_ts()}] [olho-publico-etl] {msg}", flush=True)


def _ano_mes_corrente() -> str:
    now = datetime.now(UTC)
    return f"{now.year}-{now.month:02d}"


def _run_startup_jobs(settings: Settings) -> None:
    try:
        n = run_sync_ibge(settings.database_url)
        _log(f"sync_ibge OK — {n} municipios upsertados")
    except Exception as e:  # noqa: BLE001
        _log(f"sync_ibge FALHOU: {e}")
        traceback.print_exc()


def _run_periodic_jobs(settings: Settings) -> None:
    require_settings("transparencia_api_key")
    ibge_ids = [x.strip() for x in settings.ibge_sync_list.split(",") if x.strip()]
    ano_mes = _ano_mes_corrente()
    try:
        result = run_multiplas_cidades(settings, ibge_ids, ano_mes)
        for ibge, n in result.items():
            _log(f"sync_transferencias {ibge} {ano_mes} — {n} contratos")
    except Exception as e:  # noqa: BLE001
        _log(f"sync_transferencias FALHOU: {e}")
        traceback.print_exc()


def main() -> int:
    settings = get_settings()
    _log(f"v{__version__} iniciado")
    _log(f"database_url    : {'OK' if settings.database_url else 'AUSENTE'}")
    _log(f"transparencia   : {'OK' if settings.transparencia_api_key else 'AUSENTE'}")
    _log(f"r2_account_id   : {'OK' if settings.r2_account_id else 'AUSENTE'}")
    _log(f"ibge_sync_list  : {settings.ibge_sync_list}")

    # Jobs de startup (idempotentes)
    _run_startup_jobs(settings)

    try:
        while True:
            _run_periodic_jobs(settings)
            _log(f"próximo ciclo em {JOB_INTERVAL_SECONDS // 3600}h")
            time.sleep(JOB_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        _log("encerrando por SIGINT")
        return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Validar syntax**

```bash
cd apps/etl && python -c "import olho_publico_etl.__main__"
# Expected: sem erros
```

- [ ] **Step 3: Rodar ruff + mypy nos arquivos novos**

```bash
ruff check apps/etl
# Expected: All checks passed!
```

- [ ] **Step 4: Rodar suite completa de testes**

```bash
cd apps/etl && pytest -v
# Expected: todos os testes existentes + novos passam
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/olho_publico_etl/__main__.py
git commit -m "feat(etl): __main__ roda sync_ibge no boot + sync_transferencias a cada 6h"
```

---

## Fase 2.6 — Web: ler dados reais

### Task 14: Atualizar queries e página de cidade

**Files:**
- Modify: `apps/web/lib/queries/municipios.ts`
- Create: `apps/web/lib/queries/agregacoes.ts`
- Modify: `apps/web/app/(public)/cidade/[uf]/[slug]/page.tsx`

- [ ] **Step 1: Adicionar query de agregação com fallback**

`apps/web/lib/queries/agregacoes.ts`:

```typescript
import { and, eq } from "drizzle-orm";
import { agregacoesMunicipio } from "@olho/db";
import { db } from "../db";

export async function getAgregacaoAno(municipioId: string, ano: number) {
  const rows = await db
    .select()
    .from(agregacoesMunicipio)
    .where(
      and(
        eq(agregacoesMunicipio.municipioId, municipioId),
        eq(agregacoesMunicipio.anoReferencia, ano)
      )
    )
    .limit(1);
  return rows[0] ?? null;
}
```

- [ ] **Step 2: Substituir a página `cidade/[uf]/[slug]/page.tsx`**

`apps/web/app/(public)/cidade/[uf]/[slug]/page.tsx`:

```tsx
import { notFound } from "next/navigation";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCard } from "@/components/alerts/alert-card";
import { TopFornecedores } from "@/components/city/top-fornecedores";
import { GastosPorArea } from "@/components/city/gastos-por-area";
import { ComparacaoSimilares } from "@/components/city/comparacao-similares";
import { mockMunicipios, mockAgregacoes, mockAlertasSP } from "@/lib/mock";
import { getMunicipioBySlug } from "@/lib/queries/municipios";
import { getAgregacaoAno } from "@/lib/queries/agregacoes";
import { formatBRLCompact, formatNumber } from "@olho/shared";
import { BarChart3 } from "lucide-react";

export const revalidate = 21600; // 6h ISR

interface Props {
  params: Promise<{ uf: string; slug: string }>;
}

async function loadMunicipio(uf: string, slug: string) {
  try {
    const db = await getMunicipioBySlug(uf, slug);
    if (db) return db;
  } catch {
    // Banco indisponível — cai no mock
  }
  return mockMunicipios.find((m) => m.uf === uf.toUpperCase() && m.slug === slug) ?? null;
}

async function loadAgregacao(municipioId: string) {
  const ano = new Date().getFullYear();
  try {
    const ag = await getAgregacaoAno(municipioId, ano);
    if (ag) return ag;
  } catch {
    // fallback
  }
  return mockAgregacoes[municipioId] ?? null;
}

export async function generateMetadata({ params }: Props) {
  const { uf, slug } = await params;
  const m = await loadMunicipio(uf, slug);
  if (!m) return {};
  const ag = await loadAgregacao(m.idIbge);
  const total = ag ? formatBRLCompact(ag.totalContratosFederais) : "";
  return {
    title: `${m.nome} — ${m.uf}`,
    description: total
      ? `${m.nome} (${m.uf}) recebeu ${total} em contratos federais. Veja sinais detectados e maiores fornecedores.`
      : `Dados públicos de ${m.nome}, ${m.uf}.`,
  };
}

export default async function CidadePage({ params }: Props) {
  const { uf, slug } = await params;
  const municipio = await loadMunicipio(uf, slug);
  if (!municipio) notFound();
  const agregacoes = await loadAgregacao(municipio.idIbge);
  const alertas = municipio.idIbge === "3550308" ? mockAlertasSP : [];

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <header className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <Link href="/" className="text-sm text-fg-subtle hover:text-fg">Início</Link>
          <span className="text-fg-subtle">/</span>
          <span className="text-sm text-fg-subtle">{municipio.uf}</span>
        </div>
        <h1 className="text-4xl font-bold tracking-tight">{municipio.nome}</h1>
        <p className="mt-2 text-fg-muted">
          {municipio.uf} · {formatNumber(municipio.populacao ?? 0)} habitantes
          {municipio.prefeitoNome && (
            <>
              {" "}· Prefeito(a): <span className="text-fg">{municipio.prefeitoNome}</span>
              {municipio.prefeitoPartido && ` (${municipio.prefeitoPartido})`}
            </>
          )}
        </p>
        <div className="mt-4 flex items-center gap-3">
          <Badge variant="muted">Cobertura prefeitura: {municipio.coberturaPrefeitura}</Badge>
          {municipio.erpDetectado && <Badge variant="muted">ERP: {municipio.erpDetectado}</Badge>}
          <Link href={`/cidade/${municipio.uf}/${municipio.slug}/dashboard`}>
            <Button variant="secondary" size="sm">
              <BarChart3 className="size-4 mr-2" /> Ver dashboard completo
            </Button>
          </Link>
        </div>
      </header>

      {agregacoes && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
          <KpiCard label="Contratos federais" value={formatBRLCompact(agregacoes.totalContratosFederais)} />
          <KpiCard label="Contratos prefeitura" value={formatBRLCompact(agregacoes.totalContratosPrefeitura)} />
          <KpiCard label="Total de contratos" value={formatNumber(agregacoes.qtdContratosFederais + agregacoes.qtdContratosPrefeitura)} />
          <KpiCard label="Sinais detectados" value={String(alertas.length)} highlight={alertas.length > 0} />
        </section>
      )}

      {alertas.length > 0 && (
        <section className="mb-10">
          <h2 className="text-xl font-semibold mb-4">Sinais detectados</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {alertas.map((a) => <AlertCard key={a.id} alerta={a} />)}
          </div>
        </section>
      )}

      {agregacoes && agregacoes.topFornecedores.length > 0 && (
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-10">
          <TopFornecedores items={agregacoes.topFornecedores} />
          {agregacoes.gastosPorArea.length > 0 && <GastosPorArea items={agregacoes.gastosPorArea} />}
        </section>
      )}

      {agregacoes && agregacoes.comparacaoSimilares.length > 0 && (
        <section className="mb-10">
          <ComparacaoSimilares items={agregacoes.comparacaoSimilares} />
        </section>
      )}

      {!agregacoes && (
        <div className="rounded-lg border border-dashed border-border p-8 text-center">
          <p className="text-fg-muted">
            Ainda estamos consolidando os dados desta cidade. Volte em breve.
          </p>
        </div>
      )}
    </div>
  );
}

function KpiCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="rounded-lg border border-border bg-bg-subtle p-4">
      <p className="text-xs uppercase tracking-wider text-fg-subtle">{label}</p>
      <p className={`mt-1 font-mono text-xl font-semibold ${highlight ? "text-accent-strong" : "text-fg"}`}>
        {value}
      </p>
    </div>
  );
}
```

- [ ] **Step 3: Build local para garantir compilação**

```bash
cd /Users/felipeabreu/Documents/Apps/gov
DATABASE_URL=postgresql://placeholder@localhost/x NEXT_PUBLIC_SITE_URL=http://localhost:3000 \
  pnpm --filter web build
# Expected: 10 rotas geradas sem erro
```

- [ ] **Step 4: Commit**

```bash
git add apps/web/lib/queries/ apps/web/app/\(public\)/cidade/
git commit -m "feat(web): cidade page lê DB real com fallback para mock"
```

---

## Fase 2.7 — Deploy e validação

### Task 15: Build nova imagem ETL e redeploy

**Files:** (nenhum novo — vai no CI automaticamente pelo push)

- [ ] **Step 1: Garantir que `apps/etl/pyproject.toml` inclui as deps novas**

Verificar que `pyproject.toml` tem em `[project].dependencies`:
- `httpx>=0.27.0` ✓ (já existe)
- `tenacity>=9.0.0` ✓
- `polars>=1.12.0` ✓
- `boto3>=1.35.0` ✓
- `psycopg-pool>=3.2.0` ← **adicionar se faltar**

Se faltar `psycopg-pool`, editar `apps/etl/pyproject.toml`:

```toml
dependencies = [
    # ... existentes
    "psycopg-pool>=3.2.0",
]
```

- [ ] **Step 2: Push — CI builda imagens web e etl**

```bash
git push origin main
```

Acompanhar em: https://github.com/felipeabreu2/olho-publico/actions

- [ ] **Step 3: Após CI completar, fazer Pull and redeploy no Portainer**

Stacks → `olho-publico` → Pull and redeploy.

- [ ] **Step 4: Acompanhar logs do container ETL na VPS**

```bash
# SSH na VPS
PG=$(docker ps --filter "name=olho-publico_etl" --format "{{.ID}}" | head -1)
docker logs -f $PG
```

Logs esperados:
```
[...] v0.1.0 iniciado
[...] sync_ibge OK — 5570 municipios upsertados
[...] sync_transferencias 3550308 2026-04 — NNN contratos
```

---

### Task 16: Validação end-to-end

- [ ] **Step 1: Verificar municipios no banco**

```bash
docker exec $PG_CONTAINER psql -U olho-publico -d olho_publico -c "
SELECT COUNT(*), MIN(nome), MAX(nome) FROM municipios;
"
# Expected: count=5570, min e max com nomes de cidades
```

- [ ] **Step 2: Verificar contratos federais de SP**

```bash
docker exec $PG_CONTAINER psql -U olho-publico -d olho_publico -c "
SELECT COUNT(*), SUM(valor)::numeric(20,2)
FROM contratos
WHERE municipio_aplicacao_id = '3550308' AND fonte = 'portal_transparencia';
"
# Expected: count > 0, sum > 0
```

- [ ] **Step 3: Verificar agregação de SP**

```bash
docker exec $PG_CONTAINER psql -U olho-publico -d olho_publico -c "
SELECT ano_referencia, total_contratos_federais, qtd_contratos_federais,
       jsonb_array_length(top_fornecedores) AS qtd_top
FROM agregacoes_municipio
WHERE municipio_id = '3550308';
"
# Expected: 1 linha com dados
```

- [ ] **Step 4: Abrir o site**

`https://olho.optiongrowth.com.br/cidade/SP/sao-paulo`

Verificar:
- KPIs mostram valores REAIS (não os mock)
- "Maiores fornecedores" lista CNPJs reais
- Badge de cobertura ainda "nenhuma" (esperado até P7)

- [ ] **Step 5: Commit de tag de milestone**

```bash
git tag p2-complete
git push --tags
```

---

## Self-review (executado na hora)

**Cobertura da spec:**
- ✅ Ingestão Portal da Transparência (Contratos, TODO: emendas/convênios em plano posterior)
- ✅ IBGE municípios
- ✅ Pipeline Bronze (R2 Parquet) + Gold (Postgres upsert)
- ✅ `agregacoes_municipio` recomputada
- ✅ Web lê DB real com fallback
- ⚠️ CEIS/CNEP, TSE, Compras.gov, Receita CNPJ — ficam para P3/P4 (fora do escopo explícito de P2)
- ⚠️ Alertas — P6

**Placeholders:** Nenhum encontrado — todas as queries SQL, todos os código escritos por extenso.

**Consistência de tipos:**
- `Contrato.fonte: FonteContrato` usado consistentemente ("portal_transparencia")
- `Empresa.cnpj` sempre 14 dígitos sem pontuação
- `Municipio.id_ibge` sempre 7 chars padding com zero
- Todas as funções de upsert recebem `conn` (psycopg connection) e iteráveis de modelos

**Riscos conhecidos:**
1. **Resposta real da API** pode divergir da fixture — a primeira execução em produção pode precisar de ajuste no `parse_transferencias_payload`. Mitigação: o cliente loga respostas e um erro de parsing só descarta o registro.
2. **Rate limit 90/min** pode ser baixo para muitos municípios. Mitigação: lista inicial pequena (`ibge_sync_list` default = SP), expansão gradual.
3. **Startup IBGE + sync simultâneo** pode rodar pela primeira vez com tabela municipios vazia. Mitigação: `_run_startup_jobs` roda IBGE ANTES do loop de transferências.
