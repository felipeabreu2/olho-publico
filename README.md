# Olho Público

> Plataforma pública e aberta que mostra para onde vai o dinheiro público brasileiro.

[![CI Web](https://github.com/USER/olho-publico/actions/workflows/web-ci.yml/badge.svg)](.github/workflows/web-ci.yml)
[![CI ETL](https://github.com/USER/olho-publico/actions/workflows/etl-ci.yml/badge.svg)](.github/workflows/etl-ci.yml)

Olho Público agrega dados oficiais brasileiros (Portal da Transparência, Receita Federal, TSE, CGU, IBGE e portais municipais) e os apresenta de forma simples na perspectiva da cidade. Sem opiniões — só fatos e sinais documentados.

## Status

🚧 **Em desenvolvimento ativo (V1 / MVP)**. Veja:
- [Spec de design](docs/superpowers/specs/2026-04-22-olho-publico-design.md)
- [Plano de implementação P1 — Scaffolding](docs/superpowers/plans/2026-04-22-olho-publico-p1-scaffolding.md)
- [Roadmap completo no spec, seção 11](docs/superpowers/specs/2026-04-22-olho-publico-design.md#11-roadmap)
- [Próximos passos para o usuário](docs/HANDOFF.md)

## Estrutura

```
olho-publico/
├── apps/
│   ├── web/        Next.js 15 frontend (Vercel)
│   └── etl/        Python pipelines (VPS Portainer)
├── packages/
│   ├── db/         Schema Drizzle compartilhado
│   └── shared/     Tipos e helpers TS
├── infra/          docker-compose, Caddy, Portainer
└── docs/           specs, plans, metodologia
```

## Stack

- **Frontend:** Next.js 15 + TypeScript + Tailwind + shadcn/ui (tema escuro)
- **Backend ETL:** Python 3.12 + Playwright + DuckDB + Pydantic
- **Banco:** PostgreSQL 16 + PostGIS + pg_trgm
- **Storage frio:** Cloudflare R2
- **Hospedagem:** Vercel (web) + VPS Portainer (ETL + DB) + R2 (storage)

## Setup local

```bash
# Pré-requisitos: Node 22, pnpm 9, Python 3.12, Docker

git clone https://github.com/USER/olho-publico.git
cd olho-publico
pnpm install
cp infra/.env.example infra/.env

# Sobe Postgres local (com PostGIS e extensões pré-criadas)
docker compose -f infra/docker-compose.yml up -d postgres

# Aplica schema Drizzle
pnpm db:generate
pnpm db:migrate

# Roda o site (com mock data)
pnpm dev
# → http://localhost:3000
```

Para ETL Python:

```bash
cd apps/etl
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
pytest -v
```

## Contribuir

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Bugs e sugestões: abra uma issue.

## Licença

[Source-available, não-comercial](LICENSE).
