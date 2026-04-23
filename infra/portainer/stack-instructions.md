# Subir Olho Público no Portainer

Guia para subir **TUDO** (web + ETL + Postgres + Caddy + backup) na sua VPS via Portainer.

## Pré-requisitos

- VPS com Docker + Portainer rodando (você já tem)
- Repositório no GitHub: `felipeabreu2/olho-publico`
- Imagens Docker já buildadas pelo CI no GHCR: `ghcr.io/felipeabreu2/olho-publico/web:latest` e `ghcr.io/felipeabreu2/olho-publico/etl:latest`

> **Como verificar se as imagens existem:** https://github.com/felipeabreu2?tab=packages
> Após push pra `main`, GitHub Actions builda automaticamente. Demora ~5 min na primeira vez.

## Passo a passo

### 1. Tornar as imagens públicas no GHCR (uma vez só)

Por padrão, imagens no GHCR são privadas. Para o Portainer puxar sem login:

1. Vá em https://github.com/felipeabreu2?tab=packages
2. Clique em `olho-publico/web` → **Package settings** → **Change visibility** → **Public**
3. Repita para `olho-publico/etl`

> Alternativa (se quiser manter privado): configurar registry com login no Portainer (Registries → Add → GHCR + Personal Access Token).

### 2. Criar a Stack no Portainer

1. Portainer → **Stacks** → **Add stack**
2. **Name:** `olho-publico`
3. **Build method:** escolha **Repository**
   - **Repository URL:** `https://github.com/felipeabreu2/olho-publico`
   - **Repository reference:** `refs/heads/main`
   - **Compose path:** `infra/docker-compose.prod.yml`
   - **Authentication:** não precisa (repo público)
4. **Environment variables:** clique em **Advanced mode** e cole:

```env
POSTGRES_USER=olho
POSTGRES_PASSWORD=COLOQUE_UMA_SENHA_FORTE_AQUI
SITE_URL=http://SEU_IP_DA_VPS
GITHUB_REPO=felipeabreu2/olho-publico
TRANSPARENCIA_API_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_RAW=olho-publico-raw
R2_BUCKET_BRONZE=olho-publico-bronze
R2_BUCKET_BACKUPS=olho-publico-backups
DAGSTER_PASSWORD_HASH=
```

> ETL e R2 podem ficar vazios por enquanto — o **web vai subir mesmo sem eles**, usando os dados mock que estão no código.

5. **GitOps updates** (opcional, recomendado):
   - Marque **Pull and redeploy**
   - **Polling interval:** 5 minutes
   - Assim, todo push pra `main` faz a stack pegar o código novo automaticamente.

6. Clique em **Deploy the stack**.

### 3. Aguardar containers ficarem healthy

No Portainer → **Containers**, você verá:

| Container | Status esperado |
|---|---|
| `olho-publico_postgres_1` | ✅ healthy (~30s) |
| `olho-publico_web_1` | ✅ healthy (~1min) |
| `olho-publico_caddy_1` | ✅ running |
| `olho-publico_etl_1` | ⚠️ pode dar restart loop até ter `TRANSPARENCIA_API_KEY` (normal) |
| `olho-publico_postgres-backup_1` | ✅ running (mesmo sem R2 configurado, só vai falhar no upload) |

### 4. Aplicar o schema do banco (uma vez)

Antes do site servir dados reais, o Postgres precisa do schema. Rodar uma vez:

```bash
# Da sua máquina local (ou via Portainer Console no container postgres)
docker exec -e PGPASSWORD=SUA_SENHA olho-publico_postgres_1 \
  psql -U olho -d olho_publico -c "CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE EXTENSION IF NOT EXISTS pgcrypto;"

# Aplicar migration Drizzle (da sua máquina, apontando pro Postgres da VPS)
DATABASE_URL=postgresql://olho:SUA_SENHA@IP_DA_VPS:5432/olho_publico pnpm db:migrate
```

> **Atenção firewall:** se a porta 5432 não estiver aberta para o seu IP, exponha-a temporariamente no compose ou rode `docker exec` direto no container.

### 5. Acessar o site

- **Antes de ter domínio:** `http://IP_DA_VPS` (porta 80, Caddy serve direto sem TLS)
- **Depois de configurar DNS:**
  1. Aponte `olhopublico.org` (e `www`) para o IP da VPS no Cloudflare
  2. Edite `infra/caddy/Caddyfile` — comente o `:80 {}` e descomente o bloco do domínio
  3. Commit + push → GitOps redeploya → Caddy pega TLS automático via Let's Encrypt

## Atualizar a stack

- **GitOps ligado:** push pra `main` no GitHub → Portainer detecta em até 5 min → faz pull + recreate dos containers afetados
- **Manual:** Portainer → Stacks → `olho-publico` → **Pull and redeploy**

## Logs

- Portainer → Containers → clique no container → **Logs** (ou aba **Stats** para CPU/RAM)
- Para o `web`: hits do Next.js, erros 500, etc.
- Para o `etl`: status dos jobs (vazio até P2)

## Limpar tudo

Portainer → Stacks → `olho-publico` → **Delete this stack** → marque "Remove non-persistent volumes". Postgres e backups ficam preservados se não marcar.

---

## Trocar para Vercel depois (sem perder Portainer)

Se mais tarde você quiser mover o site pro Vercel (CDN global, ISR), basta:

1. Conectar o repo no Vercel apontando pra `apps/web`
2. Variáveis: `DATABASE_URL` e `NEXT_PUBLIC_SITE_URL`
3. Apontar o domínio pro Vercel em vez da VPS
4. Comentar o serviço `web` no `docker-compose.prod.yml` (mantém só Postgres + ETL na VPS)

Os dois fluxos coexistem — o Dockerfile não estorva o Vercel.
