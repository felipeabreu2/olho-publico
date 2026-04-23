# 👁️ Olho Público

> **Para onde vai o dinheiro da sua cidade?**
> O Olho Público é uma plataforma cívica e gratuita que mostra, em linguagem simples, como o dinheiro público brasileiro é gasto — começando pela sua cidade.

[![CI Web](https://github.com/felipeabreu2/olho-publico/actions/workflows/web-ci.yml/badge.svg)](https://github.com/felipeabreu2/olho-publico/actions/workflows/web-ci.yml)
[![CI ETL](https://github.com/felipeabreu2/olho-publico/actions/workflows/etl-ci.yml/badge.svg)](https://github.com/felipeabreu2/olho-publico/actions/workflows/etl-ci.yml)
[![CodeQL](https://github.com/felipeabreu2/olho-publico/actions/workflows/codeql.yml/badge.svg)](https://github.com/felipeabreu2/olho-publico/actions/workflows/codeql.yml)
[![License: Source-Available](https://img.shields.io/badge/license-source--available-blue)](LICENSE)

---

## 🎯 Em 30 segundos

Você digita o nome da sua cidade. O site mostra:

- 💰 **Quanto** dinheiro público foi gasto ali
- 🏢 **Quais empresas** receberam mais contratos
- ⚠️ **Sinais de alerta** detectados automaticamente (empresas recém-criadas com contratos milionários, dispensas de licitação suspeitas, fornecedor que doou para o prefeito etc.)
- 📊 **Para onde** o dinheiro foi (saúde, educação, obras…)
- 🔍 **Comparação** com cidades parecidas

Tudo isso vem **só de dados oficiais públicos** (Portal da Transparência, Receita Federal, TSE, IBGE, CGU). Nenhuma opinião — só fatos e sinais com explicação.

---

## ❓ Para quem é o Olho Público

| Público | O que ganha aqui |
|---|---|
| 🧑‍🤝‍🧑 **Cidadão** | Entender em 30 segundos como o prefeito/governo gasta o dinheiro da sua cidade |
| 📰 **Jornalistas** | Cruzar bases (CNPJ × contratos × doações) para investigações |
| 🏛️ **Vereadores/oposição** | Material factual e auditável para fiscalização |
| 🎓 **Pesquisadores e acadêmicos** | Dados estruturados sobre gastos públicos brasileiros |
| ⚖️ **Compliance e due diligence** | Verificar histórico de fornecedores antes de contratar |

---

## 🤔 Por que isso importa

O Brasil tem **transparência pública por lei** (LAI — Lei 12.527/2011), mas os dados ficam espalhados em **dezenas de portais diferentes**, cada um com formato próprio, alguns só em PDF, outros sem busca decente.

Resultado: o cidadão comum não consegue responder perguntas básicas como "quem foi a empresa que mais recebeu da minha prefeitura?" sem virar pesquisador full-time.

O Olho Público faz a parte chata (baixar, limpar, cruzar e organizar tudo) e entrega a resposta pronta, com link para a fonte original.

---

## 🛡️ Princípios não-negociáveis

1. **Fato antes de opinião** — só mostramos o que está oficial. Nada de "achismo".
2. **Sinais não são acusações** — todo alerta vem com aviso e link para os dados-fonte.
3. **Cobertura nacional** — funciona para qualquer das 5.570 cidades brasileiras.
4. **Metodologia transparente** — toda regra de detecção é pública, versionada e explicada em [METODOLOGIA.md](docs/METODOLOGIA.md).
5. **Sem cadastro, sem rastreio** — você navega anonimamente.
6. **Direito de resposta** — qualquer pessoa pode contestar um dado e a resposta fica vinculada.

---

## 📍 Status do projeto

🚧 **V1 (MVP) em desenvolvimento ativo.** Roadmap completo:

| Fase | Entrega | Status |
|---|---|---|
| **V1 (MVP)** | Página de cidade com fatos + alertas (federal nacional + prefeituras via ERPs) | 🚧 Scaffolding pronto, aguardando ingestão de dados |
| **V2** | Página completa de empresa/CNPJ + score com revisão jurídica | ⏳ |
| **V3** | Página do político + cruzamentos | ⏳ |
| **V4** | Feed nacional de alertas + assinatura por email | ⏳ |
| **V5+** | Vertical jornalista (export, busca avançada) e compliance B2B | ⏳ |

📄 [Ver spec completa](docs/superpowers/specs/2026-04-22-olho-publico-design.md) · 📋 [Ver plano de implementação P1](docs/superpowers/plans/2026-04-22-olho-publico-p1-scaffolding.md) · 🚀 [Próximos passos para colocar no ar](docs/HANDOFF.md)

---

## 📚 Fontes de dados (V1)

| Fonte | Quem mantém | O que traz |
|---|---|---|
| [Portal da Transparência](https://portaldatransparencia.gov.br) | CGU | Contratos federais, transferências, servidores |
| [Receita Federal — Base CNPJ](https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica-cnpj) | RFB | Empresas, sócios, situação cadastral |
| [CEIS / CNEP](https://portaldatransparencia.gov.br/sancoes) | CGU | Empresas inidôneas e sancionadas |
| [TSE — Doações eleitorais](https://dadosabertos.tse.jus.br) | TSE | Doações por CNPJ/CPF, candidato, partido |
| [Compras.gov.br](https://compras.dados.gov.br) | ME/SERPRO | Licitações federais |
| [IBGE](https://ibge.gov.br) | IBGE | Municípios, população, IDH, geografia |
| Portais municipais | Cada prefeitura | Contratos, licitações, folha (via ERPs E&L, IPM, Betha, Equiplano) |

---

## 🏗️ Stack técnica

- **Frontend:** [Next.js 15](https://nextjs.org) + TypeScript + [Tailwind CSS](https://tailwindcss.com) + [shadcn/ui](https://ui.shadcn.com) — tema escuro, SEO server-side
- **Banco de dados:** [PostgreSQL 16](https://www.postgresql.org) + [PostGIS](https://postgis.net) (geometrias) + [pg_trgm](https://www.postgresql.org/docs/current/pgtrgm.html) (busca fuzzy)
- **ETL:** Python 3.12 + [Playwright](https://playwright.dev) (scrapers) + [DuckDB](https://duckdb.org) (transformações) + [Pydantic](https://pydantic.dev) (validação)
- **Storage frio:** [Cloudflare R2](https://www.cloudflare.com/products/r2/) (S3-compatible, sem custo de egress)
- **Hospedagem:** [Vercel](https://vercel.com) (web) + VPS [Portainer](https://www.portainer.io) (ETL + DB)
- **Observabilidade:** [Sentry](https://sentry.io) (erros) + [Plausible](https://plausible.io) (analytics privacy-first)

[ADRs e justificativas →](docs/DECISIONS.md)

---

## 📁 Como o repositório é organizado

```
olho-publico/
├── apps/
│   ├── web/              ← Site público em Next.js (vai pro Vercel)
│   └── etl/              ← Pipelines Python que baixam e processam dados (vão pro VPS)
├── packages/
│   ├── db/               ← Schema do banco em Drizzle (compartilhado)
│   └── shared/           ← Tipos e helpers TypeScript (formatadores, slug...)
├── infra/                ← docker-compose, Caddy, instruções Portainer
├── docs/                 ← Spec, planos de implementação, metodologia, ADRs
├── .github/              ← CI/CD, Dependabot, CodeQL, templates
└── docs/superpowers/     ← Spec de design e planos versionados
```

---

## 🚀 Rodar localmente (em 5 minutos)

**Pré-requisitos:** Node 22, [pnpm 9](https://pnpm.io/installation), Python 3.12, Docker.

```bash
git clone https://github.com/felipeabreu2/olho-publico.git
cd olho-publico

# Instala dependências do frontend
pnpm install

# Sobe Postgres local com PostGIS e extensões prontas
docker compose -f infra/docker-compose.yml up -d postgres

# Aplica o schema do banco
pnpm db:generate
pnpm db:migrate

# Roda o site (com dados mock — não precisa do banco para ver a UI)
pnpm dev
```

Abra **http://localhost:3000** e veja:

- 🏠 Home com busca + cidades em destaque + feed de alertas
- 🏙️ `/cidade/SP/sao-paulo` — exemplo de cidade no layout storytelling
- 📊 `/cidade/SP/sao-paulo/dashboard` — visão analítica
- 🏢 `/empresa/12345678000190` — página de empresa
- 🔎 `/busca?q=sao` — busca unificada
- 📖 `/metodologia` · `/contestar` · `/privacidade`

Para o **ETL Python**:

```bash
cd apps/etl
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
pytest -v
```

---

## 🤝 Quero contribuir

Este é um projeto cívico e aceita contribuição de:

- 👩‍💻 **Devs** — scrapers de prefeituras, melhorias de UI, testes, performance
- 📰 **Jornalistas** — propor novas regras de alerta com base em casos reais que investigaram
- 🎨 **Designers** — melhorias de acessibilidade, mobile, identidade visual
- ⚖️ **Advogados/compliance** — revisão da metodologia para reduzir risco de injúria a inocentes
- ✍️ **Redatores** — explicações em linguagem simples na metodologia

Veja o [CONTRIBUTING.md](CONTRIBUTING.md) e o [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Encontrou um dado errado? Abra uma [issue](https://github.com/felipeabreu2/olho-publico/issues/new/choose) usando o template "Reportar dado incorreto".

---

## 🔒 Segurança

Encontrou uma vulnerabilidade? **Não abra issue pública.** Veja [SECURITY.md](SECURITY.md) para reportar de forma responsável.

---

## ⚖️ Licença

[Source-available, não-comercial](LICENSE). Você pode ler, estudar, modificar e contribuir livremente. Uso comercial (revender, hospedar como serviço pago, integrar em produto comercial) requer licença separada — entre em contato.

---

## 💚 Apoie o projeto

Olho Público é desenvolvido voluntariamente. Se quer ajudar a manter os servidores rodando e expandir cobertura para mais cidades, veja as opções em [.github/FUNDING.yml](.github/FUNDING.yml).

---

<sub>Feito no Brasil 🇧🇷 com base nos princípios da Lei de Acesso à Informação.</sub>
