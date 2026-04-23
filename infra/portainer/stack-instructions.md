# Subir Olho Público no Portainer (Swarm + Traefik)

Stack pensada para o ambiente Option Growth (Traefik + rede `OptionNet`).

## Pré-requisitos no host

- Docker Swarm ativo (você já tem)
- Portainer rodando (você já tem)
- Traefik rodando como stack separada com `letsencryptresolver` no entrypoint `websecure` (você já tem — exemplo no `ollama` stack)
- Rede `OptionNet` externa criada (você já tem)
- DNS apontando o subdomínio escolhido (`olho.optiongrowth.com.br`) para o IP do Swarm manager

## ⚠️ Resolver o erro "stack already exists"

Se aparecer "A stack with the normalized name 'olho-publico' already exists", a stack anterior ficou registrada (mesmo que o deploy tenha falhado). **Antes de recriar, apague a velha:**

1. Portainer → **Stacks**
2. Achar `olho-publico` na lista (provavelmente status "limited" ou "inactive")
3. Selecionar e clicar em **Remove**
4. Confirmar — pode marcar **"Remove non-persistent volumes"** (postgres usa volume externo, não some)

Agora pode recriar.

## Passo 1 — Criar volume externo na VPS (uma vez só)

Por SSH na VPS:

```bash
docker volume create olho_publico_postgres
```

Verifique:

```bash
docker volume ls | grep olho_publico
# olho_publico_postgres  ← deve aparecer
```

> Sem isso, o Swarm reclama que o volume não existe.

## Passo 2 — Tornar imagens GHCR públicas (uma vez só)

Vai em https://github.com/felipeabreu2?tab=packages e, para cada imagem (`olho-publico/web`, `olho-publico/etl`):

- **Package settings** → **Change visibility** → **Public**

> Sem isso, Swarm não consegue fazer pull.

## Passo 3 — Criar Stack no Portainer

1. **Stacks** → **Add stack**
2. **Name:** `olho-publico`
3. **Build method:** **Repository**
   - **Repository URL:** `https://github.com/felipeabreu2/olho-publico`
   - **Repository reference:** `refs/heads/main`
   - **Compose path:** `infra/docker-compose.prod.yml`
   - **Authentication:** desligado (repo público)
4. **GitOps updates:** ligar **Pull and redeploy**, polling **5 minutes**

5. **Environment variables** → **Advanced mode** → cole:

```env
POSTGRES_USER=olho
POSTGRES_PASSWORD=COLOQUE_UMA_SENHA_FORTE_AQUI
WEB_HOST=olho.optiongrowth.com.br
SITE_URL=https://olho.optiongrowth.com.br
GITHUB_REPO=felipeabreu2/olho-publico
TRANSPARENCIA_API_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_RAW=olho-publico-raw
R2_BUCKET_BRONZE=olho-publico-bronze
R2_BUCKET_BACKUPS=olho-publico-backups
```

> Pode deixar `TRANSPARENCIA_API_KEY` e R2 vazios. O **web sobe sem eles** com mock data; só `etl` e `postgres-backup` ficam aguardando essas variáveis.

6. **Deploy the stack**

## Passo 4 — Apontar DNS

No Cloudflare (ou onde o domínio `optiongrowth.com.br` está):

- Adicionar **A record**: `olho` → IP da VPS (proxy Cloudflare opcional, Traefik pega o cert via DNS-01 ou HTTP-01)

Aguardar propagação (~1 min).

## Passo 5 — Aplicar schema do banco (uma vez)

Schema Drizzle vai no Postgres. Da sua máquina local:

```bash
# Variáveis
export POSTGRES_USER=olho
export POSTGRES_PASSWORD=SUA_SENHA

# Habilitar extensões necessárias (uma vez)
docker exec -i $(docker ps -qf "name=olho-publico_postgres") \
  psql -U $POSTGRES_USER -d olho_publico -c "
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
  "

# Aplicar migrations Drizzle (precisa de acesso de rede ao postgres)
# Opção A: rodar Drizzle de dentro de um container temporário na rede OptionNet
docker run --rm --network OptionNet \
  -v $(pwd):/work -w /work \
  node:22-alpine sh -c "
    corepack enable pnpm && \
    pnpm install --frozen-lockfile && \
    DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/olho_publico \
    pnpm db:migrate
  "

# Opção B: expor porta 5432 temporariamente no compose, rodar pnpm db:migrate
# da máquina local, e fechar a porta de volta.
```

## Passo 6 — Acessar o site

`https://olho.optiongrowth.com.br` deve renderizar o site no tema escuro.

Verificar logs no Portainer → **Containers** → `olho-publico_web.1...` → **Logs**.

## Containers esperados

| Serviço | Status esperado |
|---|---|
| `olho-publico_postgres` | ✅ healthy (~30s) |
| `olho-publico_web` | ✅ running (~1min) — Traefik começa a rotear |
| `olho-publico_etl` | ⚠️ restart loop até `TRANSPARENCIA_API_KEY` ser preenchida (normal) |
| `olho-publico_postgres-backup` | ✅ running, log `[backup] R2 não configurado — pulando` até R2 ser configurado |

## Atualizar a stack

**GitOps ligado:** push pra `main` no GitHub → Portainer detecta em até 5 min → faz pull das imagens novas e recreate dos containers afetados.

**Manual:** Portainer → Stacks → `olho-publico` → **Pull and redeploy** (botão).

## Logs e troubleshooting

| Problema | Diagnóstico |
|---|---|
| Site não carrega no domínio | DNS apontou? Traefik enxerga as labels? `docker service ls` deve mostrar `olho-publico_web` com 1/1 réplicas |
| Erro 502 Bad Gateway | Container `web` ainda subindo, ou healthcheck falhando. Ver logs do web. |
| Postgres healthy mas web em loop | Variável `DATABASE_URL` errada? Conferir `POSTGRES_USER`/`POSTGRES_PASSWORD` |
| ETL fica reiniciando | Esperado se `TRANSPARENCIA_API_KEY` estiver vazia |
| Imagem não pulla | GHCR ainda privado? Ver Passo 2 |

## Limpeza

Portainer → Stacks → `olho-publico` → **Remove**. O volume `olho_publico_postgres` é externo e fica preservado (apague manualmente com `docker volume rm olho_publico_postgres` se quiser).
