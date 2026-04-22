# Importar como Stack no Portainer

1. Portainer → Stacks → Add stack
2. Nome: `olho-publico`
3. Build method: **Repository** (apontando para o GitHub deste projeto, branch `main`)
4. Compose path: `infra/docker-compose.prod.yml`
5. Environment variables: copiar de `infra/.env.example` e preencher
6. Deploy

## Variáveis obrigatórias

- `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `TRANSPARENCIA_API_KEY` (criar em https://api.portaldatransparencia.gov.br/)
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_BACKUPS` (criar bucket no Cloudflare R2 antes)
- `GITHUB_REPO` (ex: `felipeoptiongrowth/olho-publico`)

## Firewall

- Porta 443 — pública (Caddy)
- Porta 5433 — restrita ao IP da Vercel (lista em https://vercel.com/docs/concepts/edge-network/regions)

## Aplicar migrations

Após primeira subida da stack:

```bash
docker exec -it olho-publico_postgres_1 psql -U $POSTGRES_USER -d olho_publico -c "\\dx"
# verificar que pg_trgm e pgcrypto existem; se não, criar manualmente

# Aplicar schema Drizzle (rodar em workstation com pnpm):
DATABASE_URL=postgresql://USER:PASS@postgres.olhopublico.org:5433/olho_publico pnpm db:migrate
```
