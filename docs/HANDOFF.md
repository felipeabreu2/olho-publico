# Handoff — o que falta para o Olho Público entrar no ar

> Plano P1 (scaffolding) executado autonomamente. Para destravar P2 em diante, complete os passos abaixo na ordem.

## Status atual (P1 concluído ✅)

- ✅ Monorepo pnpm + git
- ✅ Schema Drizzle completo (10 tabelas, enums, índices)
- ✅ Pacote `@olho/shared` (formatadores, slug, types) com testes
- ✅ App Next.js 15 com tema escuro, todas as 7 páginas funcionando com mock data
- ✅ Componentes UI primitivos + storytelling cards + busca
- ✅ App Python ETL com modelos Pydantic + skeleton de fontes + engine de alertas (1 regra completa, 5 skeletons)
- ✅ Docker Compose dev + prod, Caddy, instruções Portainer
- ✅ GitHub Actions CI (web + etl) + build de imagem ETL
- ✅ Documentação (README, CONTRIBUTING, LICENSE source-available, METODOLOGIA, DECISIONS)
- ✅ sitemap.xml + robots.txt com cidades-mock
- ✅ Backup script Postgres → R2

---

## 1. Contas e segredos (15 min)

- [ ] Criar repositório no GitHub: https://github.com/new (sugestão: `olho-publico`)
- [ ] Push do código local: `git remote add origin git@github.com:USER/olho-publico.git && git push -u origin main`
- [ ] Criar conta Vercel: https://vercel.com/signup (login com GitHub)
- [ ] Criar conta Cloudflare (se ainda não tem): https://dash.cloudflare.com/sign-up
- [ ] Criar conta Sentry: https://sentry.io/signup (hobby plan)

## 2. Domínio (10 min)

- [ ] Comprar domínio (sugestão: `olhopublico.org` ou `.com.br`) — Registro.br ou Namecheap
- [ ] Apontar nameservers para Cloudflare (interface do registrador)
- [ ] Adicionar domínio no Cloudflare e validar nameservers

## 3. Cloudflare R2 (10 min)

- [ ] No painel Cloudflare → R2 → Create bucket: `olho-publico-raw`
- [ ] Criar mais 2 buckets: `olho-publico-bronze`, `olho-publico-backups`
- [ ] R2 → Manage R2 API tokens → Create token (Read/Write em todos os 3 buckets)
- [ ] Anotar: Account ID, Access Key ID, Secret Access Key
- [ ] Editar `infra/.env` na VPS com esses valores

## 4. VPS — Postgres + ETL (30 min)

- [ ] SSH na VPS
- [ ] Garantir Docker e Portainer rodando
- [ ] Em Portainer → Stacks → Add stack:
  - Nome: `olho-publico`
  - Build method: Repository (apontando para o GitHub deste projeto)
  - Compose path: `infra/docker-compose.prod.yml`
  - Variáveis de ambiente: copiar de `infra/.env.example` e preencher
  - Deploy
- [ ] Aguardar Postgres ficar healthy
- [ ] Aplicar migration: rodar `pnpm db:generate && pnpm db:migrate` localmente apontando `DATABASE_URL` para o Postgres da VPS

## 5. Vercel (15 min)

- [ ] No Vercel → Add new project → Import o repositório GitHub
- [ ] Root directory: `apps/web`
- [ ] Framework: Next.js (auto-detect)
- [ ] Variáveis de ambiente:
  - `DATABASE_URL=postgresql://USER:PASS@postgres.olhopublico.org:5433/olho_publico?sslmode=require`
  - `NEXT_PUBLIC_SITE_URL=https://olhopublico.org`
- [ ] Deploy
- [ ] Vercel → Settings → Domains → adicionar `olhopublico.org` (e `www.olhopublico.org`)

## 6. Portal da Transparência API (10 min)

- [ ] Cadastrar em https://api.portaldatransparencia.gov.br/swagger-ui.html
- [ ] Solicitar chave (precisa CPF brasileiro)
- [ ] Adicionar `TRANSPARENCIA_API_KEY` no `.env` da VPS

## 7. Próximos passos com o Claude

Com tudo acima pronto, abra uma nova sessão do Claude e diga:

> "Estou pronto para executar o plano P2 (Ingestão Portal da Transparência) — todas as credenciais foram configuradas."

Eu vou então:
1. Escrever o plano P2 detalhado (TDD, task por task)
2. Executar a ingestão real
3. Substituir os mocks por dados reais nas páginas
4. Seguir para P3 em diante (Receita CNPJ, sanções, doações, alertas, prefeituras)

## Anexos

- [Spec completa de V1](superpowers/specs/2026-04-22-olho-publico-design.md)
- [Plano P1 (executado)](superpowers/plans/2026-04-22-olho-publico-p1-scaffolding.md)
- [Metodologia](METODOLOGIA.md)
- [ADRs](DECISIONS.md)

## Ver o site rodando agora (com mocks)

```bash
cd /Users/felipeabreu/Documents/Apps/gov
pnpm install
pnpm dev
```

Abra http://localhost:3000 — você verá:
- Home com busca + 3 cidades em destaque + 3 alertas
- `/cidade/SP/sao-paulo` (storytelling completo)
- `/cidade/SP/sao-paulo/dashboard`
- `/empresa/12345678000190`
- `/busca?q=sao`
- `/metodologia`, `/contestar`, `/privacidade`
