# Decisões de arquitetura (ADRs)

## ADR 001 — Monorepo pnpm

Adotamos monorepo `pnpm workspaces` para que `apps/web`, `apps/etl` e `packages/*` compartilhem types/schema sem publicar pacotes. Trade-off: requer pnpm específico.

## ADR 002 — Lakehouse com R2 frio + Postgres quente

Em vez de carregar toda a base bruta no Postgres (estouraria o disco da VPS), gravamos raw e Parquet no Cloudflare R2 e mantemos no Postgres apenas a camada Gold (dados prontos para servir). DuckDB lê Parquet do R2 quando necessário.

## ADR 003 — Self-host Postgres na VPS Portainer

Supabase free não cabe (500 MB; nosso Gold projeta 3-15 GB). Pro custaria $25/mês. VPS já paga, com 16 GB RAM e 80 GB disco, é capaz com folga. Mitigamos backups com `pg_dump` diário pro R2.

## ADR 004 — Sem autenticação no MVP

Todo conteúdo é público. Reduz superfície de ataque, simplifica LGPD, melhora cache. Auth entra apenas em V5+ se vertical compliance/jornalista exigir.

## ADR 005 — Estratégia de cobertura de prefeituras via ERPs

Em vez de scraper por município (5.570), atacamos por ERP comum (E&L, IPM, Betha, Equiplano). Cada scraper construído libera centenas de cidades.

## ADR 006 — Sem score em V1

Score/nota traz risco legal alto e exige metodologia defensável. V1 mostra apenas fatos e sinais com disclaimer; score entra em V2 com revisão jurídica.

## ADR 007 — UX por cidade, não por CNPJ

Cidadão sabe nome da cidade, não CNPJ. Entrada do produto é busca por município; CNPJ é função secundária. Internamente, base técnica continua sendo CNPJ-centric.

## ADR 008 — Layout storytelling principal + dashboard secundário

Página de cidade prioriza cards narrativos (B). Quem quer escavar acessa rota `/dashboard` com KPIs e tabelas (A). Combina viralização com profundidade.
