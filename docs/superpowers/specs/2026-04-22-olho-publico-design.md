# Olho Público — Documento de Design (V1 / MVP)

**Data:** 2026-04-22
**Status:** Aprovado para planejamento de implementação
**Autor:** Felipe Abreu (Option Growth) com auxílio de Claude Code

---

## 1. Visão

**Olho Público** é uma plataforma pública e aberta que mostra, em linguagem simples, **para onde vai o dinheiro público brasileiro**, começando pela perspectiva da cidade. O cidadão digita o nome da própria cidade e recebe, em segundos, um feed de fatos relevantes e sinais automatizados de irregularidade — sempre baseados em dados oficiais.

A V1 é o primeiro passo de uma plataforma maior: a base técnica construída para alimentar a "página da cidade" também alimentará, em fases posteriores, páginas de empresa, político e um feed nacional de alertas em tempo real.

### Objetivos da V1

1. Lançar em **3 a 4 meses** um portal público acessível em qualquer dispositivo
2. Cobrir as **5.570 cidades brasileiras** com dados federais
3. Cobrir **um conjunto inicial de cidades** com dados das prefeituras (via integração com ERPs municipais comuns)
4. Manter custo de infraestrutura **abaixo de US$ 30/mês** durante o MVP, reaproveitando VPS existente
5. Estabelecer reputação de seriedade jornalística — sem opiniões, só fatos e sinais bem documentados

### Não-objetivos da V1

- Sistema de score/nota para cidades, empresas ou políticos (fica para V2 com revisão jurídica)
- Página completa de empresa/CNPJ (versão leve apenas; completa fica para V2)
- Página de político (V3)
- Feed nacional de alertas em tempo real (V4)
- Autenticação, contas de usuário, personalização
- Vertical jornalista (export avançado, busca cruzada) ou compliance (B2B)

---

## 2. Princípios não-negociáveis

1. **Fato antes de opinião.** V1 mostra apenas fatos oficiais agregados e sinais marcados explicitamente como "sinais", não acusações.
2. **Cidadão entende em 30 segundos.** Layout principal é storytelling em cards com linguagem simples; dashboard analítico fica como porta secundária.
3. **Cobertura nacional desde o dia 1.** Qualquer brasileiro digita sua cidade e vê algo relevante (mesmo cidades pequenas, via dados federais).
4. **Transparência da metodologia.** Toda regra de alerta, toda fonte e todo cálculo é documentado, versionado em público e linkado a partir das páginas que o usam.
5. **Custo controlado.** Projeto cívico bootstrap; arquitetura precisa custar centavos por mês no MVP.
6. **Sem coleta de dados pessoais do visitante.** Sem login, sem tracking identificável; analytics privacy-first.

---

## 3. Público e modelo

- **Público da V1:** cidadão comum buscando entender sua cidade.
- **Públicos futuros (V2+):** jornalistas (V2 pela página da empresa), políticos/candidatos sob escrutínio público (V3), área de compliance B2B (V5+).
- **Modelo de licença:** **source-available** (código público, não-comercial). Permite contribuição cívica e auditabilidade da metodologia, mantendo direito futuro de monetização em vertical B2B.
- **Identidade visual:** moderno/tech — fundo escuro, tipografia geométrica (estilo Linear/Vercel). Comunica competência técnica e seriedade sem o peso institucional.
- **Nome:** **Olho Público**.

---

## 4. Arquitetura de alto nível

```
┌─────────────────────────────────────────────────────────┐
│                  USUÁRIO (navegador)                    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────┐
│  VERCEL — Next.js 15 (App Router, SSR + ISR)            │
│  ├─ Páginas públicas (cidade, empresa, busca, sobre)    │
│  ├─ Route Handlers (API leve, rate-limited por IP)      │
│  └─ Cache de página por cidade (revalida a cada 6h)     │
└────────────────────────┬────────────────────────────────┘
                         │ SQL (Postgres protocol) via TLS
                         ▼
┌─────────────────────────────────────────────────────────┐
│  VPS PORTAINER (8 vCPU / 16 GB / 80 GB / 20 TB)         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Caddy (reverse proxy + TLS automático)         │   │
│  └────────┬────────────────────────────────┬───────┘   │
│           ▼                                ▼           │
│  ┌─────────────────┐          ┌──────────────────────┐ │
│  │  PostgreSQL 16  │          │  ETL containers      │ │
│  │  (camada Gold)  │◀─────────│  Python 3.12         │ │
│  │  + PostGIS      │  bulk    │  + Playwright        │ │
│  │  + pg_trgm      │  insert  │  + DuckDB            │ │
│  └────────┬────────┘          │  + Pydantic          │ │
│           │                   │  + Dagster (orq.)    │ │
│           │                   └──────┬───────────────┘ │
└───────────┼──────────────────────────┼─────────────────┘
            │ pg_dump diário           │ download / parse
            ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│  CLOUDFLARE R2 (storage)                                │
│  ├─ raw/         (ZIPs originais — auditoria/replay)    │
│  ├─ bronze/      (Parquet limpo, particionado por ano)  │
│  └─ backups/     (dumps diários do Postgres)            │
└─────────────────────────────────────────────────────────┘
```

### Por que essa arquitetura

- **Frontend separado em Vercel:** SEO crítico (cada cidade precisa rankear no Google quando alguém busca "[cidade] gastos"); ISR regenera páginas periodicamente sem custo por request; build em Vercel é trivial; CDN global.
- **Backend self-host na VPS:** o usuário já paga a VPS; ETL pesado (Receita CNPJ 45 GB, scrapers Playwright) não cabe em serverless; Postgres na mesma máquina permite bulk insert local sem latência de rede.
- **Lakehouse (R2 frio + Postgres quente):** dados brutos e Parquet ficam no R2 (centavos/mês, ilimitado); Postgres mantém apenas a camada "Gold" pronta para servir (~3-15 GB), cabendo folgado nos 80 GB da VPS.
- **DuckDB nos containers ETL:** lê Parquet direto do R2 para recomputar agregações sem precisar carregar tudo em RAM.

### Camadas de dados (medallion simplificado)

| Camada | Onde | Conteúdo | Atualização |
|---|---|---|---|
| **Raw** | R2 `raw/` | ZIPs/CSVs originais imutáveis | Sob demanda do scheduler |
| **Bronze** | R2 `bronze/` | Parquet limpo, tipado, particionado por ano/mês | Após cada execução de scraper |
| **Gold** | Postgres na VPS | Tabelas agregadas e denormalizadas, prontas para servir | Após Bronze, em transação atômica |

---

## 5. Stack técnica

### Frontend
- **Next.js 15** (App Router) + **TypeScript**
- **Tailwind CSS** + **shadcn/ui** (tema escuro custom)
- **Drizzle ORM** (acessa Postgres via Postgres protocol; migrations versionadas em TS)
- **Zod** (validação de inputs)
- Hospedagem: **Vercel** (Hobby no início; Pro quando crescer)

### Backend / ETL (na VPS via Portainer)
- **Python 3.12** com:
  - **httpx** — chamadas a APIs públicas (Portal da Transparência, Compras.gov)
  - **Playwright** — scrapers de portais municipais com JavaScript pesado
  - **DuckDB** — transformações analíticas (lê Parquet do R2, escreve Parquet no R2)
  - **Pydantic** — validação dos modelos de dados ingeridos
  - **psycopg[binary,pool]** — conexão Postgres
  - **brutils** + **python-stdnum** — validação de CNPJ/CPF brasileiros
- **Dagster** para orquestração e observabilidade (UI mostra status de cada job, retries, alertas em falha) — começar com cron simples se a complexidade for baixa nas primeiras semanas
- Containers definidos em `docker-compose.yml` versionado no Git, importados como Stack no Portainer

### Banco de dados
- **PostgreSQL 16** self-host na VPS (container Portainer)
- Extensões: **PostGIS** (geometrias municipais), **pg_trgm** (busca fuzzy), **pgcrypto** (UUIDs)
- Backup: `pg_dump` compactado diário enviado para R2 `backups/`
- Conexão do Vercel via **Postgres protocol over TLS** (Caddy expõe porta segura, IP allow-list)

### Storage
- **Cloudflare R2** — S3-compatible, sem custo de egress
  - `raw/` — arquivos originais imutáveis
  - `bronze/` — Parquet processado
  - `backups/` — dumps diários

### Observability e operações
- **Sentry** (hobby) — erros frontend e backend
- **Plausible Analytics** — analytics privacy-friendly, sem cookies (self-host depois no Portainer ou SaaS)
- **Caddy** — reverse proxy com TLS automático (Let's Encrypt)
- **GitHub Actions** — CI/CD (lint, test, deploy do frontend; build de imagens Docker para o ETL)

### Custo estimado (V1)

| Item | Custo mensal |
|---|---|
| Vercel Hobby | $0 (Pro $20 quando crescer) |
| VPS (já paga) | $0 incremental |
| Cloudflare R2 (~50 GB armazenamento) | ~$1 |
| Sentry hobby | $0 |
| Plausible | $0 (self-host) ou $9 (SaaS) |
| Domínio `.com.br` ou `.org` | ~$15/ano |
| **Total incremental** | **$1-30/mês** |

---

## 6. Modelo de dados (camada Gold no Postgres)

Tabelas principais — esquema resumido. Detalhes finais ficam para a fase de implementação.

### `municipios`
- ~5.570 linhas (uma por município brasileiro)
- Colunas: `id_ibge` (PK), `nome`, `slug`, `uf`, `populacao`, `idh`, `geometria` (PostGIS), `prefeito_nome`, `prefeito_partido`, `cobertura_prefeitura` (enum: `nenhuma | parcial | completa`), `erp_detectado`
- Índices: `uf`, `slug`, `nome` (trigram para busca fuzzy)

### `empresas`
- Apenas CNPJs que aparecem em alguma fonte (~800k inicialmente, pode crescer)
- Colunas: `cnpj` (PK, 14 dígitos), `razao_social`, `nome_fantasia`, `data_abertura`, `situacao`, `cnae_principal`, `municipio_sede` (FK), `flags` (JSONB: `{sancionada: true, doadora: true, ...}`)
- Índices: trigram em `razao_social`, GIN em `flags`

### `socios`
- Vínculo CNPJ ↔ pessoa
- Colunas: `cnpj` (FK), `cpf_mascarado` (`***.123.456-**`), `nome`, `tipo` (sócio, administrador), `data_entrada`
- Sócios aparecem como "pessoa" sem identificação completa para LGPD

### `contratos`
- Denormalizado, indexado para busca por município ou CNPJ
- Colunas: `id`, `municipio_aplicacao_id` (FK), `cnpj_fornecedor`, `orgao_contratante`, `objeto`, `valor`, `data_assinatura`, `modalidade_licitacao`, `fonte` (enum), `dados_originais_url`
- Índices: `(municipio_aplicacao_id, data_assinatura DESC)`, `cnpj_fornecedor`, GIN em `objeto` (FTS português)

### `sancoes`
- CEIS/CNEP com vínculo CNPJ
- Colunas: `id`, `cnpj`, `tipo_sancao`, `orgao_sancionador`, `data_inicio`, `data_fim`, `motivo`, `fonte_url`

### `doacoes`
- TSE, doações eleitorais
- Colunas: `id`, `cnpj_doador` (nullable), `cpf_doador_mascarado` (nullable), `candidato_nome`, `candidato_cargo`, `partido`, `valor`, `ano_eleicao`, `municipio_id` (FK quando aplicável)

### `agregacoes_municipio`
- Pré-computadas para servir a página da cidade em <50 ms
- Colunas: `municipio_id` (PK), `ano_referencia`, `total_contratos_federais`, `total_contratos_prefeitura`, `top_fornecedores` (JSONB array), `gastos_por_area` (JSONB), `comparacao_similares` (JSONB), `atualizado_em`
- Recomputada após cada ingestão por job DuckDB → SQL `INSERT ... ON CONFLICT DO UPDATE`

### `alertas`
- Alertas detectados pelas regras
- Colunas: `id`, `tipo` (FK para `regras_alerta.codigo`), `severidade` (`info | atencao | forte`), `municipio_id` (FK), `cnpj_envolvido` (nullable), `evidencia` (JSONB), `data_deteccao`, `regra_versao` (string semver)
- Índices: `(municipio_id, data_deteccao DESC)`

### `regras_alerta`
- Definição versionada das regras
- Colunas: `codigo` (PK), `nome`, `descricao`, `versao_atual`, `parametros` (JSONB), `disclaimer_text`, `criada_em`, `atualizada_em`
- Vista alternativa em `metodologia.md` no repo, sincronizada via CI

### `contestacoes`
- Fila de moderação dos formulários "contestar dado"
- Colunas: `id`, `tipo_alvo` (`alerta | contrato | empresa | municipio`), `id_alvo`, `email_solicitante`, `mensagem`, `status` (`pendente | em_analise | respondida | arquivada`), `resposta`, `data_solicitacao`, `data_resposta`

---

## 7. Pipeline ETL — fontes da V1

| Fonte | O que traz | Frequência | Volume aprox. | Como ingerimos |
|---|---|---|---|---|
| **Portal da Transparência (CGU)** | Contratos federais, convênios, transferências, servidores federais | Diária (incremental) | ~5 GB total | API REST oficial (com chave gratuita) |
| **Receita Federal — Base CNPJ** | Empresas, sócios, situação cadastral, CNAE, Simples | Mensal | 45 GB compactado | Download mensal de dados.gov.br + parse com DuckDB |
| **CEIS / CNEP (CGU)** | Empresas inidôneas e sancionadas | Semanal | ~50 MB | Download CSV oficial |
| **TSE — Doações eleitorais** | Doações por CNPJ/CPF, candidato, partido | Por eleição (anual em ano eleitoral) | ~3 GB | Download por eleição em dados.tse.jus.br |
| **Compras.gov.br** | Licitações federais | Diária | ~2 GB total | API REST oficial |
| **IBGE** | Municípios, população, IDH, geometrias | Anual | ~100 MB | Download CSV/Shapefile |
| **ERPs de prefeitura** (E&L, IPM, Betha, Equiplano) | Contratos, licitações, folha das prefeituras cobertas | Diária por município ativo | varia | Scraper Python (httpx ou Playwright) por ERP, parametrizado por município |

### Estratégia para prefeituras (escolha confirmada: ERPs)

Em vez de scraper individual por cidade, construímos **um scraper por ERP**. Cada scraper é parametrizado pelo município (URL base, código municipal). Detectar qual ERP cada município usa: análise prévia da página inicial do portal de transparência da cidade.

**Cobertura projetada:** os 4 ERPs prioritários (E&L, IPM, Betha, Equiplano) cobrem aproximadamente **2.000 municípios** quando todos os scrapers estiverem prontos. Meta de V1: lançar com pelo menos **2 ERPs prontos** cobrindo 800-1.200 cidades, mais expansão incremental nos meses seguintes.

### Confiabilidade dos scrapers

- Cada job grava status, contagem de registros e erros estruturados
- Dagster detecta falhas e envia alerta (email/webhook); execuções com queda de >30% no volume disparam alerta automático
- Versão original (Raw) sempre arquivada antes de qualquer parse — permite reprocessar quando o parser quebra

---

## 8. Engenharia de alertas (Tipo 2 do feed)

Cada alerta carrega `tipo`, `severidade`, `evidencia` (JSONB com fonte e cálculo), `disclaimer` e link para a página de metodologia da regra.

### Regras iniciais V1 (versionadas em código + documentadas em `metodologia.md`)

| Código | Nome | Severidade padrão | Lógica |
|---|---|---|---|
| `EMPRESA_FOGUETE` | Empresa-foguete | Forte | CNPJ aberto há <12 meses recebeu contrato >R$ 500k |
| `DISPENSA_SUSPEITA` | Dispensa de licitação relevante | Atenção | Contrato sem licitação acima de R$ 1M |
| `SOCIO_SANCIONADO` | Sócio em lista de sanções | Forte | Empresa com contrato cujo sócio aparece em CEIS/CNEP |
| `CRESCIMENTO_ANOMALO` | Crescimento anômalo em receita pública | Atenção | Empresa cujo faturamento público cresceu >300% ano a ano |
| `CONCENTRACAO` | Concentração de fornecedor | Info | Mesma empresa = >40% dos contratos de uma secretaria |
| `DOADOR_BENEFICIADO` | Doador da campanha do prefeito | Atenção | Empresa que doou para campanha do prefeito atual recebeu contrato após eleição |

### Disclaimer obrigatório em todos os alertas

> "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação, conclusão investigativa ou imputação de irregularidade. Veja a metodologia completa e os dados-fonte para análise contextualizada."

### Versionamento

Toda mudança de regra (novo limiar, novo cálculo) gera **nova versão semver** registrada em `regras_alerta.versao_atual`. Alertas antigos mantêm referência à versão usada na detecção. Mudanças relevantes anunciadas em `/metodologia`.

---

## 9. UX e páginas do MVP

### Layout principal: storytelling escuro/tech

- Fundo escuro (`#0a0a0a` / `#111`)
- Acentos: verde `#10b981` (fato neutro), âmbar `#f59e0b` (atenção), vermelho `#ef4444` (sinal forte)
- Tipografia: **Inter** (UI) + **JetBrains Mono** (números/dados)
- Componentes-base: shadcn/ui customizado

### Páginas

| Rota | Conteúdo |
|---|---|
| `/` | Busca grande no centro ("Digite sua cidade ou um CNPJ"), feed nacional de alertas em destaque, cards de cidades em foco |
| `/cidade/[uf]/[slug]` | Layout B (storytelling) — cabeçalho, alertas, top fornecedores, gastos por área, comparação com cidades similares; botão "ver dashboard completo" |
| `/cidade/[uf]/[slug]/dashboard` | Layout A — KPIs, gráficos, tabelas exportáveis |
| `/empresa/[cnpj]` | V1 leve — dados cadastrais + contratos + sanções + doações |
| `/busca?q=` | Resultados unificados (cidade + empresa) |
| `/metodologia` | Fontes, regras de alerta versionadas, equipe, doação, contato |
| `/contestar` | Formulário público de contestação (com captcha) |
| `/api/v1/...` | JSON dos dados (rate-limited por IP) |

### Performance e SEO

- Páginas de cidade pré-renderizadas via **ISR** (Incremental Static Regeneration), revalidação a cada 6h
- Open Graph caprichado por página (gera imagem dinâmica via `@vercel/og`) — para WhatsApp e Twitter virarem viral
- Meta descrição dinâmica com fato-âncora ("Em 2025, [cidade] recebeu R$ X em contratos federais; 3 alertas detectados")
- Sitemap.xml auto-gerado contendo todas as 5.570 cidades

---

## 10. Tratamento legal e LGPD

- **Apenas dados públicos** já oficialmente disponibilizados pelos órgãos competentes (Lei 12.527 — LAI)
- **CPFs sempre mascarados** (`***.123.456-**`) quando aparecem em doações ou sócios
- **Sem coleta de dados pessoais do visitante** (sem login, sem tracking, analytics privacy-first)
- Único dado pessoal coletado: email (opcional) de quem usa o formulário de contestação ou, futuramente em V4, assinatura de alertas — sempre com base legal de consentimento revogável
- **Disclaimer permanente** em todos os alertas (texto na seção 8)
- **Direito de resposta** — toda página de empresa, cidade ou alerta tem botão "contestar dado"; resposta oficial fica vinculada ao registro
- **Termos de uso** explicando finalidade jornalística/cívica
- **Auditoria** — toda regra versionada no Git; histórico público de mudanças metodológicas
- **Política de privacidade** clara em `/privacidade`, em linguagem simples

---

## 11. Roadmap

| Fase | Entrega | Duração |
|---|---|---|
| **V1 (MVP)** | Cidade (federal nacional + prefeituras via 2-4 ERPs) com fatos + alertas + dashboard | 3-4 meses |
| **V2** | Página completa de empresa/CNPJ + score metodológico (com revisão jurídica prévia) | +2 meses |
| **V3** | Página do político + cruzamentos político ↔ empresa ↔ cidade | +2 meses |
| **V4** | Feed nacional de alertas em tempo real + assinatura por cidade via email (double opt-in, sem conta) | +3 meses |
| **V5+** | Vertical jornalista (export, busca avançada, API ampliada) e vertical compliance (B2B) — momento de adicionar autenticação se necessário | conforme tração |

---

## 12. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| **Scrapers de prefeitura quebram quando portal muda** | Dagster com alertas em queda de volume; raw arquivado para reprocessar; cobertura distribuída por ERP minimiza impacto de uma quebra |
| **Receita CNPJ atualização rompe layout de parse** | Versionamento de schemas Pydantic; pipeline tem etapa "validar schema" antes de carregar Bronze |
| **Falsos positivos de alerta geram processo judicial** | Disclaimers fortes; severidade conservadora; direito de resposta integrado; revisão metodológica trimestral; sem score em V1 |
| **VPS com disco esgotando** | Monitoramento de disco; estratégia lakehouse mantém Postgres enxuto; storage frio em R2 ilimitado |
| **Tráfego viral sobrecarrega VPS Postgres** | Páginas servidas via ISR (cache no Vercel/CDN); VPS recebe tráfego de leitura proporcionalmente baixo |
| **Custos do Vercel explodem com viralização** | Hobby suporta MVP; plano Pro $20/mês cobre crescimento até cerca de 1M visitas/mês; cache agressivo nas páginas |
| **LGPD em sócios pessoa física (CPF)** | CPF sempre mascarado; nome de sócio disponível apenas como já está em base pública oficial; documentação clara em política de privacidade |

---

## 13. Critérios de aceite da V1

- [ ] Toda cidade brasileira (5.570) acessível via `/cidade/[uf]/[slug]` com pelo menos dados federais carregados
- [ ] Pelo menos 2 ERPs municipais integrados, cobrindo 800+ cidades com dados de prefeitura
- [ ] Pelo menos 6 regras de alerta funcionando, versionadas e documentadas em `/metodologia`
- [ ] Página da cidade carrega em <1.5 s no 4G médio (Lighthouse mobile ≥ 85 em performance)
- [ ] Backup diário do Postgres confirmado no R2 com restore testado
- [ ] Custo total de infra incremental ≤ US$ 30/mês durante MVP
- [ ] Política de privacidade, termos e metodologia publicados antes do anúncio público
- [ ] Formulário de contestação funcional com captcha e moderação manual
- [ ] Open Graph caprichado em todas as páginas de cidade
- [ ] Sitemap.xml com as 5.570 cidades publicado e submetido ao Google Search Console

---

## 14. Decisões registradas

| # | Decisão | Justificativa |
|---|---|---|
| 1 | MVP foca em cidadão (não jornalista nem compliance) | Maior potencial viral; fundação reusável para outros públicos |
| 2 | Entrada do produto é **cidade**, não CNPJ | Cidadão sabe nome da cidade, não decora CNPJ |
| 3 | Layout principal é storytelling (B), com dashboard (A) acessível | Cidadão entende em 30 s; quem quer escavar tem para onde ir |
| 4 | V1 inclui **fatos + alertas**, mas **não score** | Sweet spot de tração + risco legal aceitável; score requer revisão jurídica |
| 5 | Cobertura de prefeituras via **estratégia de ERPs** | Cada scraper construído libera centenas de cidades; melhor ROI técnico |
| 6 | Stack: Next.js Vercel + Python ETL Portainer + Postgres self-host na VPS + R2 | Aproveita VPS já paga; arquitetura lakehouse cabe nos 80 GB de disco |
| 7 | Postgres self-host (não Supabase) na V1 | Free não cabe (500 MB); Pro custa $25/mês; VPS resolve com $0 incremental |
| 8 | **Sem autenticação no MVP** | Site é 100% público; LGPD trivial; arquitetura mais simples; auth entra só em V5+ |
| 9 | Licença **source-available** (não-comercial) | Atrai contribuição cívica; preserva monetização futura B2B |
| 10 | Identidade visual **moderno/tech** (escuro, geométrico) | Sinaliza competência técnica e seriedade sem peso institucional |
| 11 | Nome **Olho Público** | Direto, brasileiro, sugere fiscalização sem agredir |
