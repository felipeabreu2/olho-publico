# Olho Público — Plano P1: Scaffolding e Dev Environment

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a fundação técnica completa do projeto Olho Público — repositório monorepo, app Next.js com páginas e componentes UI rodando com mock data, projeto Python ETL com modelos e estrutura, schema Drizzle versionado, infraestrutura Docker para a VPS, CI/CD básico e toda a documentação de handoff.

**Architecture:** Monorepo pnpm com apps separados (`apps/web` Next.js, `apps/etl` Python). Pacotes compartilhados em `packages/` (schema, types). Infra Docker em `infra/`. Tudo pronto para receber dados reais nas próximas fases sem refatoração estrutural.

**Tech Stack:** pnpm workspaces · Next.js 15 + TypeScript + Tailwind + shadcn/ui · Drizzle ORM · Python 3.12 + uv + Pydantic + DuckDB · Docker Compose · Caddy · GitHub Actions · Vitest · Playwright · Pytest

---

## Estrutura do repositório

```
gov/
├── apps/
│   ├── web/                          # Next.js frontend (Vercel)
│   │   ├── app/                      # App Router
│   │   │   ├── (public)/             # Layout público
│   │   │   │   ├── page.tsx          # Home
│   │   │   │   ├── busca/page.tsx
│   │   │   │   ├── cidade/[uf]/[slug]/
│   │   │   │   │   ├── page.tsx      # Página storytelling
│   │   │   │   │   └── dashboard/page.tsx
│   │   │   │   ├── empresa/[cnpj]/page.tsx
│   │   │   │   ├── metodologia/page.tsx
│   │   │   │   ├── contestar/page.tsx
│   │   │   │   └── privacidade/page.tsx
│   │   │   ├── api/v1/               # API pública
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn primitives
│   │   │   ├── layout/               # Header, Footer, Nav
│   │   │   ├── search/               # Busca unificada
│   │   │   ├── city/                 # Cards storytelling
│   │   │   ├── dashboard/            # Widgets dashboard
│   │   │   ├── alerts/               # AlertCard com disclaimer
│   │   │   └── shared/               # MoneyDisplay, CnpjDisplay, etc.
│   │   ├── lib/
│   │   │   ├── db.ts                 # Cliente Drizzle
│   │   │   ├── queries/              # Queries SQL tipadas
│   │   │   ├── mock/                 # Dados mock para dev
│   │   │   ├── format.ts             # Formatação BRL, CNPJ, datas
│   │   │   └── seo.ts                # Helpers Open Graph
│   │   ├── public/
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   └── e2e/
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   └── package.json
│   └── etl/                          # Python ETL (VPS Portainer)
│       ├── olho_publico_etl/
│       │   ├── __init__.py
│       │   ├── config.py             # Settings via Pydantic
│       │   ├── models/               # Pydantic models por entidade
│       │   │   ├── municipio.py
│       │   │   ├── empresa.py
│       │   │   ├── contrato.py
│       │   │   ├── sancao.py
│       │   │   ├── doacao.py
│       │   │   └── alerta.py
│       │   ├── sources/              # Conectores por fonte
│       │   │   ├── base.py           # Source ABC
│       │   │   ├── transparencia/    # Portal da Transparência (skeleton)
│       │   │   ├── receita/          # Receita CNPJ (skeleton)
│       │   │   ├── ceis_cnep/
│       │   │   ├── tse/
│       │   │   ├── compras/
│       │   │   ├── ibge/
│       │   │   └── prefeituras/      # ERPs (skeleton por ERP)
│       │   │       ├── el/
│       │   │       ├── ipm/
│       │   │       ├── betha/
│       │   │       └── equiplano/
│       │   ├── pipeline/             # Bronze → Gold loaders
│       │   │   ├── bronze.py         # Parquet writer (R2)
│       │   │   └── gold.py           # Postgres loader
│       │   ├── alerts/               # Engine de alertas
│       │   │   ├── engine.py
│       │   │   └── rules/            # Cada regra um arquivo
│       │   │       ├── empresa_foguete.py
│       │   │       ├── dispensa_suspeita.py
│       │   │       ├── socio_sancionado.py
│       │   │       ├── crescimento_anomalo.py
│       │   │       ├── concentracao.py
│       │   │       └── doador_beneficiado.py
│       │   ├── storage/              # R2 client wrapper
│       │   ├── db/                   # Postgres client
│       │   └── utils/
│       │       ├── cpf_mask.py
│       │       └── slug.py
│       ├── tests/
│       │   ├── unit/
│       │   └── fixtures/
│       ├── pyproject.toml
│       ├── Dockerfile
│       └── README.md
├── packages/
│   ├── db/                           # Schema Drizzle compartilhado
│   │   ├── schema/
│   │   │   ├── municipios.ts
│   │   │   ├── empresas.ts
│   │   │   ├── socios.ts
│   │   │   ├── contratos.ts
│   │   │   ├── sancoes.ts
│   │   │   ├── doacoes.ts
│   │   │   ├── agregacoes.ts
│   │   │   ├── alertas.ts
│   │   │   ├── regras_alerta.ts
│   │   │   ├── contestacoes.ts
│   │   │   └── index.ts              # re-export
│   │   ├── migrations/               # gerado por drizzle-kit
│   │   ├── drizzle.config.ts
│   │   ├── tsconfig.json
│   │   └── package.json
│   └── shared/                       # Types/utils compartilhados
│       ├── src/
│       │   ├── types.ts
│       │   ├── format.ts
│       │   └── slug.ts
│       └── package.json
├── infra/
│   ├── docker-compose.yml            # dev local: Postgres + ETL
│   ├── docker-compose.prod.yml       # produção VPS
│   ├── caddy/
│   │   └── Caddyfile
│   └── portainer/
│       └── stack-instructions.md
├── docs/
│   ├── superpowers/
│   │   ├── specs/
│   │   └── plans/
│   ├── METODOLOGIA.md
│   ├── HANDOFF.md                    # checklist de tarefas para o usuário
│   ├── DECISIONS.md                  # ADRs
│   └── PRIVACIDADE.md
├── .github/
│   └── workflows/
│       ├── web-ci.yml
│       └── etl-ci.yml
├── .gitignore
├── README.md
├── CONTRIBUTING.md
├── LICENSE                           # source-available custom
├── pnpm-workspace.yaml
├── package.json
└── .editorconfig
```

---

## Fase 1.1 — Inicialização do repositório

### Task 1: Git + .gitignore + EditorConfig

**Files:**
- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `README.md` (placeholder mínimo, expandido depois)

- [ ] **Step 1: Inicializar git repo**

```bash
cd /Users/felipeabreu/Documents/Apps/gov
git init -b main
```

- [ ] **Step 2: Criar .gitignore**

```
# Dependências
node_modules/
.pnpm-store/
__pycache__/
*.pyc
.venv/
venv/

# Build
.next/
dist/
build/
*.tsbuildinfo

# Env e segredos
.env
.env.local
.env.*.local
!.env.example

# Logs
*.log
npm-debug.log*
pnpm-debug.log*

# Editor
.vscode/
.idea/
.DS_Store

# Dados locais
data/
*.parquet
*.duckdb

# Brainstorm/superpowers state
.superpowers/
```

- [ ] **Step 3: Criar .editorconfig**

```
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true

[*.py]
indent_size = 4

[*.md]
trim_trailing_whitespace = false
```

- [ ] **Step 4: README placeholder**

```markdown
# Olho Público

Plataforma pública e aberta que mostra para onde vai o dinheiro público brasileiro.

> Em desenvolvimento ativo. Veja `docs/superpowers/specs/2026-04-22-olho-publico-design.md`.
```

- [ ] **Step 5: Commit inicial**

```bash
git add .gitignore .editorconfig README.md
git commit -m "chore: bootstrap project (gitignore, editorconfig, readme)"
```

---

### Task 2: Monorepo pnpm

**Files:**
- Create: `package.json` (root)
- Create: `pnpm-workspace.yaml`

- [ ] **Step 1: Criar pnpm-workspace.yaml**

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

- [ ] **Step 2: Criar package.json root**

```json
{
  "name": "olho-publico",
  "version": "0.1.0",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "scripts": {
    "dev": "pnpm --filter web dev",
    "build": "pnpm -r build",
    "lint": "pnpm -r lint",
    "test": "pnpm -r test",
    "typecheck": "pnpm -r typecheck",
    "db:generate": "pnpm --filter @olho/db generate",
    "db:migrate": "pnpm --filter @olho/db migrate"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "prettier": "^3.3.0"
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add package.json pnpm-workspace.yaml
git commit -m "chore: setup pnpm monorepo"
```

---

## Fase 1.2 — Pacote `packages/db` (Drizzle Schema)

### Task 3: Configuração Drizzle

**Files:**
- Create: `packages/db/package.json`
- Create: `packages/db/tsconfig.json`
- Create: `packages/db/drizzle.config.ts`

- [ ] **Step 1: package.json**

```json
{
  "name": "@olho/db",
  "version": "0.1.0",
  "private": true,
  "main": "./schema/index.ts",
  "types": "./schema/index.ts",
  "scripts": {
    "generate": "drizzle-kit generate",
    "migrate": "drizzle-kit migrate",
    "studio": "drizzle-kit studio",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "drizzle-orm": "^0.36.0",
    "postgres": "^3.4.0"
  },
  "devDependencies": {
    "drizzle-kit": "^0.28.0",
    "@types/node": "^22.0.0",
    "typescript": "^5.6.0"
  }
}
```

- [ ] **Step 2: tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "noEmit": true
  },
  "include": ["schema/**/*", "drizzle.config.ts"]
}
```

- [ ] **Step 3: drizzle.config.ts**

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./schema/index.ts",
  out: "./migrations",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL ?? "postgresql://postgres:postgres@localhost:5432/olho_publico",
  },
  verbose: true,
  strict: true,
});
```

- [ ] **Step 4: Commit**

```bash
git add packages/db/
git commit -m "chore(db): setup drizzle config"
```

---

### Task 4: Schema — municipios

**Files:**
- Create: `packages/db/schema/municipios.ts`

- [ ] **Step 1: Definir schema**

```typescript
import { pgTable, varchar, integer, text, real, timestamp, pgEnum, index } from "drizzle-orm/pg-core";

export const coberturaPrefeituraEnum = pgEnum("cobertura_prefeitura", [
  "nenhuma",
  "parcial",
  "completa",
]);

export const municipios = pgTable(
  "municipios",
  {
    idIbge: varchar("id_ibge", { length: 7 }).primaryKey(),
    nome: text("nome").notNull(),
    slug: varchar("slug", { length: 120 }).notNull().unique(),
    uf: varchar("uf", { length: 2 }).notNull(),
    populacao: integer("populacao"),
    idh: real("idh"),
    geometria: text("geometria"),
    prefeitoNome: text("prefeito_nome"),
    prefeitoPartido: varchar("prefeito_partido", { length: 20 }),
    coberturaPrefeitura: coberturaPrefeituraEnum("cobertura_prefeitura").notNull().default("nenhuma"),
    erpDetectado: varchar("erp_detectado", { length: 30 }),
    atualizadoEm: timestamp("atualizado_em", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => ({
    ufIdx: index("idx_municipios_uf").on(t.uf),
    nomeIdx: index("idx_municipios_nome_trgm").using("gin", t.nome),
  })
);

export type Municipio = typeof municipios.$inferSelect;
export type MunicipioInsert = typeof municipios.$inferInsert;
```

- [ ] **Step 2: Commit**

```bash
git add packages/db/schema/municipios.ts
git commit -m "feat(db): municipios schema with PostGIS-ready geometria column"
```

---

### Task 5: Schema — empresas + socios

**Files:**
- Create: `packages/db/schema/empresas.ts`
- Create: `packages/db/schema/socios.ts`

- [ ] **Step 1: empresas.ts**

```typescript
import { pgTable, varchar, text, date, jsonb, timestamp, index } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";

export const empresas = pgTable(
  "empresas",
  {
    cnpj: varchar("cnpj", { length: 14 }).primaryKey(),
    razaoSocial: text("razao_social").notNull(),
    nomeFantasia: text("nome_fantasia"),
    dataAbertura: date("data_abertura"),
    situacao: varchar("situacao", { length: 30 }),
    cnaePrincipal: varchar("cnae_principal", { length: 7 }),
    municipioSedeId: varchar("municipio_sede_id", { length: 7 }).references(() => municipios.idIbge),
    flags: jsonb("flags").$type<Record<string, boolean>>().default({}).notNull(),
    atualizadoEm: timestamp("atualizado_em", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => ({
    razaoSocialIdx: index("idx_empresas_razao_social_trgm").using("gin", t.razaoSocial),
    flagsIdx: index("idx_empresas_flags").using("gin", t.flags),
    sedeIdx: index("idx_empresas_sede").on(t.municipioSedeId),
  })
);

export type Empresa = typeof empresas.$inferSelect;
export type EmpresaInsert = typeof empresas.$inferInsert;
```

- [ ] **Step 2: socios.ts**

```typescript
import { pgTable, varchar, text, date, serial, index } from "drizzle-orm/pg-core";
import { empresas } from "./empresas";

export const socios = pgTable(
  "socios",
  {
    id: serial("id").primaryKey(),
    cnpj: varchar("cnpj", { length: 14 }).notNull().references(() => empresas.cnpj, { onDelete: "cascade" }),
    cpfMascarado: varchar("cpf_mascarado", { length: 14 }),
    nome: text("nome").notNull(),
    tipo: varchar("tipo", { length: 30 }),
    dataEntrada: date("data_entrada"),
  },
  (t) => ({
    cnpjIdx: index("idx_socios_cnpj").on(t.cnpj),
    nomeIdx: index("idx_socios_nome_trgm").using("gin", t.nome),
  })
);

export type Socio = typeof socios.$inferSelect;
export type SocioInsert = typeof socios.$inferInsert;
```

- [ ] **Step 3: Commit**

```bash
git add packages/db/schema/empresas.ts packages/db/schema/socios.ts
git commit -m "feat(db): empresas e socios schema com CPF mascarado"
```

---

### Task 6: Schema — contratos

**Files:**
- Create: `packages/db/schema/contratos.ts`

- [ ] **Step 1: contratos.ts**

```typescript
import { pgTable, varchar, text, date, numeric, serial, pgEnum, index } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";
import { empresas } from "./empresas";

export const fonteContratoEnum = pgEnum("fonte_contrato", [
  "portal_transparencia",
  "compras_gov",
  "prefeitura_el",
  "prefeitura_ipm",
  "prefeitura_betha",
  "prefeitura_equiplano",
]);

export const contratos = pgTable(
  "contratos",
  {
    id: serial("id").primaryKey(),
    municipioAplicacaoId: varchar("municipio_aplicacao_id", { length: 7 }).references(() => municipios.idIbge),
    cnpjFornecedor: varchar("cnpj_fornecedor", { length: 14 }).references(() => empresas.cnpj),
    orgaoContratante: text("orgao_contratante").notNull(),
    objeto: text("objeto").notNull(),
    valor: numeric("valor", { precision: 18, scale: 2 }).notNull(),
    dataAssinatura: date("data_assinatura").notNull(),
    modalidadeLicitacao: varchar("modalidade_licitacao", { length: 50 }),
    fonte: fonteContratoEnum("fonte").notNull(),
    dadosOriginaisUrl: text("dados_originais_url"),
  },
  (t) => ({
    municipioDataIdx: index("idx_contratos_municipio_data").on(t.municipioAplicacaoId, t.dataAssinatura),
    fornecedorIdx: index("idx_contratos_fornecedor").on(t.cnpjFornecedor),
    objetoFtsIdx: index("idx_contratos_objeto_fts").using("gin", t.objeto),
  })
);

export type Contrato = typeof contratos.$inferSelect;
export type ContratoInsert = typeof contratos.$inferInsert;
```

- [ ] **Step 2: Commit**

```bash
git add packages/db/schema/contratos.ts
git commit -m "feat(db): contratos schema com índice por município+data"
```

---

### Task 7: Schema — sancoes, doacoes

**Files:**
- Create: `packages/db/schema/sancoes.ts`
- Create: `packages/db/schema/doacoes.ts`

- [ ] **Step 1: sancoes.ts**

```typescript
import { pgTable, varchar, text, date, serial, index } from "drizzle-orm/pg-core";
import { empresas } from "./empresas";

export const sancoes = pgTable(
  "sancoes",
  {
    id: serial("id").primaryKey(),
    cnpj: varchar("cnpj", { length: 14 }).notNull().references(() => empresas.cnpj),
    tipoSancao: varchar("tipo_sancao", { length: 50 }).notNull(),
    orgaoSancionador: text("orgao_sancionador").notNull(),
    dataInicio: date("data_inicio").notNull(),
    dataFim: date("data_fim"),
    motivo: text("motivo"),
    fonteUrl: text("fonte_url"),
  },
  (t) => ({
    cnpjIdx: index("idx_sancoes_cnpj").on(t.cnpj),
  })
);

export type Sancao = typeof sancoes.$inferSelect;
export type SancaoInsert = typeof sancoes.$inferInsert;
```

- [ ] **Step 2: doacoes.ts**

```typescript
import { pgTable, varchar, text, integer, numeric, serial, index } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";

export const doacoes = pgTable(
  "doacoes",
  {
    id: serial("id").primaryKey(),
    cnpjDoador: varchar("cnpj_doador", { length: 14 }),
    cpfDoadorMascarado: varchar("cpf_doador_mascarado", { length: 14 }),
    candidatoNome: text("candidato_nome").notNull(),
    candidatoCargo: varchar("candidato_cargo", { length: 50 }).notNull(),
    partido: varchar("partido", { length: 20 }),
    valor: numeric("valor", { precision: 18, scale: 2 }).notNull(),
    anoEleicao: integer("ano_eleicao").notNull(),
    municipioId: varchar("municipio_id", { length: 7 }).references(() => municipios.idIbge),
  },
  (t) => ({
    cnpjIdx: index("idx_doacoes_cnpj").on(t.cnpjDoador),
    candidatoIdx: index("idx_doacoes_candidato").on(t.candidatoNome),
    municipioAnoIdx: index("idx_doacoes_municipio_ano").on(t.municipioId, t.anoEleicao),
  })
);

export type Doacao = typeof doacoes.$inferSelect;
export type DoacaoInsert = typeof doacoes.$inferInsert;
```

- [ ] **Step 3: Commit**

```bash
git add packages/db/schema/sancoes.ts packages/db/schema/doacoes.ts
git commit -m "feat(db): sancoes e doacoes schema"
```

---

### Task 8: Schema — agregacoes_municipio, alertas, regras_alerta, contestacoes

**Files:**
- Create: `packages/db/schema/agregacoes.ts`
- Create: `packages/db/schema/alertas.ts`
- Create: `packages/db/schema/regras_alerta.ts`
- Create: `packages/db/schema/contestacoes.ts`
- Create: `packages/db/schema/index.ts`

- [ ] **Step 1: agregacoes.ts**

```typescript
import { pgTable, varchar, integer, numeric, jsonb, timestamp, primaryKey } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";

export interface TopFornecedor {
  cnpj: string;
  razaoSocial: string;
  totalContratos: number;
  valorTotal: string;
}

export interface GastosPorArea {
  area: string;
  valor: string;
  percentual: number;
}

export interface ComparacaoSimilar {
  municipioId: string;
  municipioNome: string;
  uf: string;
  metric: string;
  valorComparado: string;
}

export const agregacoesMunicipio = pgTable(
  "agregacoes_municipio",
  {
    municipioId: varchar("municipio_id", { length: 7 }).notNull().references(() => municipios.idIbge),
    anoReferencia: integer("ano_referencia").notNull(),
    totalContratosFederais: numeric("total_contratos_federais", { precision: 18, scale: 2 }).default("0").notNull(),
    totalContratosPrefeitura: numeric("total_contratos_prefeitura", { precision: 18, scale: 2 }).default("0").notNull(),
    qtdContratosFederais: integer("qtd_contratos_federais").default(0).notNull(),
    qtdContratosPrefeitura: integer("qtd_contratos_prefeitura").default(0).notNull(),
    topFornecedores: jsonb("top_fornecedores").$type<TopFornecedor[]>().default([]).notNull(),
    gastosPorArea: jsonb("gastos_por_area").$type<GastosPorArea[]>().default([]).notNull(),
    comparacaoSimilares: jsonb("comparacao_similares").$type<ComparacaoSimilar[]>().default([]).notNull(),
    atualizadoEm: timestamp("atualizado_em", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => ({
    pk: primaryKey({ columns: [t.municipioId, t.anoReferencia] }),
  })
);

export type AgregacaoMunicipio = typeof agregacoesMunicipio.$inferSelect;
export type AgregacaoMunicipioInsert = typeof agregacoesMunicipio.$inferInsert;
```

- [ ] **Step 2: regras_alerta.ts**

```typescript
import { pgTable, varchar, text, jsonb, timestamp } from "drizzle-orm/pg-core";

export const regrasAlerta = pgTable("regras_alerta", {
  codigo: varchar("codigo", { length: 50 }).primaryKey(),
  nome: text("nome").notNull(),
  descricao: text("descricao").notNull(),
  versaoAtual: varchar("versao_atual", { length: 20 }).notNull(),
  parametros: jsonb("parametros").$type<Record<string, unknown>>().default({}).notNull(),
  disclaimerText: text("disclaimer_text").notNull(),
  criadaEm: timestamp("criada_em", { withTimezone: true }).defaultNow().notNull(),
  atualizadaEm: timestamp("atualizada_em", { withTimezone: true }).defaultNow().notNull(),
});

export type RegraAlerta = typeof regrasAlerta.$inferSelect;
export type RegraAlertaInsert = typeof regrasAlerta.$inferInsert;
```

- [ ] **Step 3: alertas.ts**

```typescript
import { pgTable, varchar, jsonb, timestamp, serial, pgEnum, index } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";
import { empresas } from "./empresas";
import { regrasAlerta } from "./regras_alerta";

export const severidadeEnum = pgEnum("severidade_alerta", ["info", "atencao", "forte"]);

export const alertas = pgTable(
  "alertas",
  {
    id: serial("id").primaryKey(),
    tipo: varchar("tipo", { length: 50 }).notNull().references(() => regrasAlerta.codigo),
    severidade: severidadeEnum("severidade").notNull(),
    municipioId: varchar("municipio_id", { length: 7 }).references(() => municipios.idIbge),
    cnpjEnvolvido: varchar("cnpj_envolvido", { length: 14 }).references(() => empresas.cnpj),
    evidencia: jsonb("evidencia").$type<Record<string, unknown>>().notNull(),
    dataDeteccao: timestamp("data_deteccao", { withTimezone: true }).defaultNow().notNull(),
    regraVersao: varchar("regra_versao", { length: 20 }).notNull(),
  },
  (t) => ({
    municipioDataIdx: index("idx_alertas_municipio_data").on(t.municipioId, t.dataDeteccao),
    cnpjIdx: index("idx_alertas_cnpj").on(t.cnpjEnvolvido),
  })
);

export type Alerta = typeof alertas.$inferSelect;
export type AlertaInsert = typeof alertas.$inferInsert;
```

- [ ] **Step 4: contestacoes.ts**

```typescript
import { pgTable, varchar, text, integer, timestamp, serial, pgEnum } from "drizzle-orm/pg-core";

export const tipoAlvoEnum = pgEnum("tipo_alvo_contestacao", ["alerta", "contrato", "empresa", "municipio"]);
export const statusContestacaoEnum = pgEnum("status_contestacao", [
  "pendente",
  "em_analise",
  "respondida",
  "arquivada",
]);

export const contestacoes = pgTable("contestacoes", {
  id: serial("id").primaryKey(),
  tipoAlvo: tipoAlvoEnum("tipo_alvo").notNull(),
  idAlvo: text("id_alvo").notNull(),
  emailSolicitante: text("email_solicitante").notNull(),
  mensagem: text("mensagem").notNull(),
  status: statusContestacaoEnum("status").notNull().default("pendente"),
  resposta: text("resposta"),
  dataSolicitacao: timestamp("data_solicitacao", { withTimezone: true }).defaultNow().notNull(),
  dataResposta: timestamp("data_resposta", { withTimezone: true }),
});

export type Contestacao = typeof contestacoes.$inferSelect;
export type ContestacaoInsert = typeof contestacoes.$inferInsert;
```

- [ ] **Step 5: index.ts (barrel)**

```typescript
export * from "./municipios";
export * from "./empresas";
export * from "./socios";
export * from "./contratos";
export * from "./sancoes";
export * from "./doacoes";
export * from "./agregacoes";
export * from "./regras_alerta";
export * from "./alertas";
export * from "./contestacoes";
```

- [ ] **Step 6: Commit**

```bash
git add packages/db/schema/
git commit -m "feat(db): agregacoes, alertas, regras e contestacoes schema"
```

---

### Task 9: Migration inicial

**Files:**
- Run: `pnpm install` (na raiz)
- Run: `pnpm db:generate`

- [ ] **Step 1: Instalar dependências**

```bash
cd /Users/felipeabreu/Documents/Apps/gov
pnpm install
```

Expected: pnpm cria `node_modules/` e instala drizzle-orm, drizzle-kit, etc.

- [ ] **Step 2: Gerar migration inicial**

```bash
pnpm db:generate
```

Expected: cria `packages/db/migrations/0000_*.sql` com todo o schema.

- [ ] **Step 3: Commit**

```bash
git add pnpm-lock.yaml packages/db/migrations/
git commit -m "feat(db): initial migration with full V1 schema"
```

---

## Fase 1.3 — Pacote `packages/shared`

### Task 10: Tipos e utils compartilhados

**Files:**
- Create: `packages/shared/package.json`
- Create: `packages/shared/tsconfig.json`
- Create: `packages/shared/src/format.ts`
- Create: `packages/shared/src/slug.ts`
- Create: `packages/shared/src/types.ts`
- Create: `packages/shared/src/index.ts`

- [ ] **Step 1: package.json**

```json
{
  "name": "@olho/shared",
  "version": "0.1.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  },
  "devDependencies": {
    "vitest": "^2.1.0",
    "typescript": "^5.6.0",
    "@types/node": "^22.0.0"
  }
}
```

- [ ] **Step 2: tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noEmit": true
  },
  "include": ["src/**/*"]
}
```

- [ ] **Step 3: src/format.ts**

```typescript
const BRL = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 2,
});

const COMPACT_BRL = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  notation: "compact",
  maximumFractionDigits: 1,
});

export function formatBRL(value: number | string): string {
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(n)) return "—";
  return BRL.format(n);
}

export function formatBRLCompact(value: number | string): string {
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(n)) return "—";
  return COMPACT_BRL.format(n);
}

export function formatCNPJ(cnpj: string): string {
  const digits = cnpj.replace(/\D/g, "").padStart(14, "0");
  return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
}

export function formatDate(input: string | Date): string {
  const d = typeof input === "string" ? new Date(input) : input;
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(d);
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("pt-BR").format(n);
}
```

- [ ] **Step 4: src/slug.ts**

```typescript
export function slugify(input: string): string {
  return input
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
```

- [ ] **Step 5: src/types.ts**

```typescript
export type UF =
  | "AC" | "AL" | "AP" | "AM" | "BA" | "CE" | "DF" | "ES" | "GO"
  | "MA" | "MT" | "MS" | "MG" | "PA" | "PB" | "PR" | "PE" | "PI"
  | "RJ" | "RN" | "RS" | "RO" | "RR" | "SC" | "SP" | "SE" | "TO";

export type SeveridadeAlerta = "info" | "atencao" | "forte";

export interface AlertaDisplay {
  id: number;
  tipo: string;
  tituloLegivel: string;
  resumoLegivel: string;
  severidade: SeveridadeAlerta;
  dataDeteccao: string;
  evidencia: Record<string, unknown>;
  disclaimer: string;
  metodologiaUrl: string;
}
```

- [ ] **Step 6: src/index.ts**

```typescript
export * from "./format";
export * from "./slug";
export * from "./types";
```

- [ ] **Step 7: Test format**

Create `packages/shared/src/format.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { formatBRL, formatBRLCompact, formatCNPJ, slugify } from "./index";

describe("formatBRL", () => {
  it("formats large values", () => {
    expect(formatBRL(1234567.89)).toMatch(/R\$\s?1\.234\.567,89/);
  });
  it("returns em-dash for NaN", () => {
    expect(formatBRL("abc")).toBe("—");
  });
});

describe("formatCNPJ", () => {
  it("masks bare digits", () => {
    expect(formatCNPJ("12345678000190")).toBe("12.345.678/0001-90");
  });
});

describe("slugify", () => {
  it("removes accents and lowercases", () => {
    expect(slugify("São Paulo")).toBe("sao-paulo");
  });
  it("handles dashes", () => {
    expect(slugify("Itabaiana - SE")).toBe("itabaiana-se");
  });
});
```

- [ ] **Step 8: Run tests**

```bash
cd packages/shared && pnpm test
```

Expected: 5 tests pass.

- [ ] **Step 9: Commit**

```bash
git add packages/shared/
git commit -m "feat(shared): format helpers, slugify and types with tests"
```

---

## Fase 1.4 — App `apps/web` (Next.js)

### Task 11: Bootstrap Next.js

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/tailwind.config.ts`
- Create: `apps/web/postcss.config.js`
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/globals.css`
- Create: `apps/web/.env.example`

- [ ] **Step 1: package.json**

```json
{
  "name": "web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --turbo",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@olho/db": "workspace:*",
    "@olho/shared": "workspace:*",
    "drizzle-orm": "^0.36.0",
    "postgres": "^3.4.0",
    "zod": "^3.23.0",
    "lucide-react": "^0.460.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0",
    "class-variance-authority": "^0.7.0",
    "@vercel/og": "^0.6.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "typescript": "^5.6.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0",
    "vitest": "^2.1.0",
    "@playwright/test": "^1.48.0"
  }
}
```

- [ ] **Step 2: tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 3: next.config.ts**

```typescript
import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
  images: {
    formats: ["image/avif", "image/webp"],
  },
};

export default config;
```

- [ ] **Step 4: tailwind.config.ts**

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0a0a0a",
          subtle: "#111111",
          elevated: "#171717",
        },
        border: {
          DEFAULT: "#262626",
          subtle: "#1f1f1f",
        },
        fg: {
          DEFAULT: "#fafafa",
          muted: "#a3a3a3",
          subtle: "#737373",
        },
        accent: {
          fact: "#10b981",
          attention: "#f59e0b",
          strong: "#ef4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
```

- [ ] **Step 5: postcss.config.js**

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 6: app/globals.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    color-scheme: dark;
  }
  body {
    @apply bg-bg text-fg font-sans antialiased;
  }
}
```

- [ ] **Step 7: app/layout.tsx**

```tsx
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: {
    default: "Olho Público — para onde vai o dinheiro público brasileiro",
    template: "%s · Olho Público",
  },
  description:
    "Plataforma pública e aberta que mostra como o dinheiro público é gasto na sua cidade.",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
  openGraph: {
    locale: "pt_BR",
    type: "website",
    siteName: "Olho Público",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 8: .env.example**

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/olho_publico
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

- [ ] **Step 9: Install + run dev**

```bash
cd /Users/felipeabreu/Documents/Apps/gov && pnpm install
cd apps/web && pnpm dev
```

Expected: Next.js sobe em http://localhost:3000 (página padrão por enquanto).

- [ ] **Step 10: Commit**

```bash
cd /Users/felipeabreu/Documents/Apps/gov
git add apps/web/
git commit -m "feat(web): bootstrap Next.js 15 with Tailwind dark theme"
```

---

### Task 12: Cliente DB e queries tipadas

**Files:**
- Create: `apps/web/lib/db.ts`
- Create: `apps/web/lib/queries/municipios.ts`
- Create: `apps/web/lib/queries/empresas.ts`

- [ ] **Step 1: lib/db.ts**

```typescript
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "@olho/db";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is not set");
}

const client = postgres(connectionString, {
  max: 10,
  idle_timeout: 20,
});

export const db = drizzle(client, { schema });
export type DB = typeof db;
```

- [ ] **Step 2: lib/queries/municipios.ts**

```typescript
import { eq, and } from "drizzle-orm";
import { db } from "../db";
import { municipios, agregacoesMunicipio, alertas } from "@olho/db";

export async function getMunicipioBySlug(uf: string, slug: string) {
  const rows = await db
    .select()
    .from(municipios)
    .where(and(eq(municipios.uf, uf.toUpperCase()), eq(municipios.slug, slug)))
    .limit(1);
  return rows[0] ?? null;
}

export async function getAgregacoesMunicipio(municipioId: string, ano: number) {
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

export async function getAlertasRecentesMunicipio(municipioId: string, limit = 10) {
  return db
    .select()
    .from(alertas)
    .where(eq(alertas.municipioId, municipioId))
    .orderBy(alertas.dataDeteccao)
    .limit(limit);
}
```

- [ ] **Step 3: lib/queries/empresas.ts**

```typescript
import { eq } from "drizzle-orm";
import { db } from "../db";
import { empresas, contratos, sancoes, doacoes } from "@olho/db";

export async function getEmpresaByCnpj(cnpj: string) {
  const rows = await db.select().from(empresas).where(eq(empresas.cnpj, cnpj)).limit(1);
  return rows[0] ?? null;
}

export async function getContratosEmpresa(cnpj: string, limit = 50) {
  return db
    .select()
    .from(contratos)
    .where(eq(contratos.cnpjFornecedor, cnpj))
    .orderBy(contratos.dataAssinatura)
    .limit(limit);
}

export async function getSancoesEmpresa(cnpj: string) {
  return db.select().from(sancoes).where(eq(sancoes.cnpj, cnpj));
}

export async function getDoacoesEmpresa(cnpj: string) {
  return db.select().from(doacoes).where(eq(doacoes.cnpjDoador, cnpj));
}
```

- [ ] **Step 4: Commit**

```bash
git add apps/web/lib/
git commit -m "feat(web): drizzle client and typed queries"
```

---

### Task 13: Mock data para desenvolvimento

**Files:**
- Create: `apps/web/lib/mock/municipios.ts`
- Create: `apps/web/lib/mock/empresas.ts`
- Create: `apps/web/lib/mock/alertas.ts`
- Create: `apps/web/lib/mock/index.ts`

- [ ] **Step 1: mock/municipios.ts**

```typescript
import type { Municipio, AgregacaoMunicipio } from "@olho/db";

export const mockMunicipios: Municipio[] = [
  {
    idIbge: "3550308",
    nome: "São Paulo",
    slug: "sao-paulo",
    uf: "SP",
    populacao: 12325232,
    idh: 0.805,
    geometria: null,
    prefeitoNome: "Ricardo Nunes",
    prefeitoPartido: "MDB",
    coberturaPrefeitura: "parcial",
    erpDetectado: "el",
    atualizadoEm: new Date(),
  },
  {
    idIbge: "2611606",
    nome: "Recife",
    slug: "recife",
    uf: "PE",
    populacao: 1488920,
    idh: 0.772,
    geometria: null,
    prefeitoNome: "João Campos",
    prefeitoPartido: "PSB",
    coberturaPrefeitura: "parcial",
    erpDetectado: "betha",
    atualizadoEm: new Date(),
  },
  {
    idIbge: "2802502",
    nome: "Itabaiana",
    slug: "itabaiana",
    uf: "SE",
    populacao: 96776,
    idh: 0.642,
    geometria: null,
    prefeitoNome: "Adailton de Souza",
    prefeitoPartido: "PP",
    coberturaPrefeitura: "nenhuma",
    erpDetectado: null,
    atualizadoEm: new Date(),
  },
];

export const mockAgregacoes: Record<string, AgregacaoMunicipio> = {
  "3550308": {
    municipioId: "3550308",
    anoReferencia: 2025,
    totalContratosFederais: "8420000000",
    totalContratosPrefeitura: "12300000000",
    qtdContratosFederais: 4821,
    qtdContratosPrefeitura: 8026,
    topFornecedores: [
      { cnpj: "12345678000190", razaoSocial: "Construtora Alpha S.A.", totalContratos: 38, valorTotal: "342000000" },
      { cnpj: "23456789000101", razaoSocial: "Limpeza Total Serviços Ltda", totalContratos: 12, valorTotal: "184000000" },
      { cnpj: "34567890000112", razaoSocial: "Tech Solutions Brasil", totalContratos: 27, valorTotal: "98000000" },
    ],
    gastosPorArea: [
      { area: "Saúde", valor: "4200000000", percentual: 38 },
      { area: "Educação", valor: "3100000000", percentual: 28 },
      { area: "Obras e Infraestrutura", valor: "2400000000", percentual: 22 },
      { area: "Administração", valor: "880000000", percentual: 8 },
      { area: "Outros", valor: "440000000", percentual: 4 },
    ],
    comparacaoSimilares: [
      { municipioId: "3304557", municipioNome: "Rio de Janeiro", uf: "RJ", metric: "gasto_per_capita", valorComparado: "0.94" },
      { municipioId: "3106200", municipioNome: "Belo Horizonte", uf: "MG", metric: "gasto_per_capita", valorComparado: "1.12" },
    ],
    atualizadoEm: new Date(),
  },
};
```

- [ ] **Step 2: mock/empresas.ts**

```typescript
import type { Empresa } from "@olho/db";

export const mockEmpresas: Empresa[] = [
  {
    cnpj: "12345678000190",
    razaoSocial: "Construtora Alpha S.A.",
    nomeFantasia: "Alpha Construções",
    dataAbertura: "1998-03-15",
    situacao: "ATIVA",
    cnaePrincipal: "4120400",
    municipioSedeId: "3550308",
    flags: { sancionada: false, doadora: true },
    atualizadoEm: new Date(),
  },
  {
    cnpj: "99887766000155",
    razaoSocial: "Servicos Express Ltda",
    nomeFantasia: null,
    dataAbertura: "2025-01-08",
    situacao: "ATIVA",
    cnaePrincipal: "8230001",
    municipioSedeId: "3550308",
    flags: { sancionada: false, doadora: false, foguete: true },
    atualizadoEm: new Date(),
  },
];
```

- [ ] **Step 3: mock/alertas.ts**

```typescript
import type { AlertaDisplay } from "@olho/shared";

export const mockAlertasSP: AlertaDisplay[] = [
  {
    id: 1,
    tipo: "EMPRESA_FOGUETE",
    tituloLegivel: "Empresa criada há 4 meses recebeu contrato de R$ 12 milhões",
    resumoLegivel:
      "Servicos Express Ltda (CNPJ 99.887.766/0001-55), aberta em janeiro/2025, foi contratada pela Secretaria de Obras de São Paulo em 08/04/2026, sem licitação.",
    severidade: "forte",
    dataDeteccao: "2026-04-22T10:00:00Z",
    evidencia: {
      cnpj: "99887766000155",
      data_abertura: "2025-01-08",
      contrato_id: 102341,
      valor: 12000000,
      modalidade: "DISPENSA",
    },
    disclaimer:
      "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa.",
    metodologiaUrl: "/metodologia#empresa-foguete",
  },
  {
    id: 2,
    tipo: "CONCENTRACAO",
    tituloLegivel: "Construtora Alpha responde por 47% dos contratos da Secretaria de Obras",
    resumoLegivel:
      "Em 2025, a empresa concentra quase metade dos contratos da pasta. Padrão pode indicar dependência ou favorecimento — exige análise detalhada.",
    severidade: "atencao",
    dataDeteccao: "2026-04-15T08:30:00Z",
    evidencia: { cnpj: "12345678000190", percentual: 47, secretaria: "Obras" },
    disclaimer:
      "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa.",
    metodologiaUrl: "/metodologia#concentracao",
  },
  {
    id: 3,
    tipo: "DOADOR_BENEFICIADO",
    tituloLegivel: "Construtora Alpha doou R$ 480 mil para campanha do prefeito atual em 2024",
    resumoLegivel:
      "A mesma empresa que doou para a campanha do prefeito recebeu 38 contratos da prefeitura em 2025, totalizando R$ 342 milhões.",
    severidade: "atencao",
    dataDeteccao: "2026-04-10T14:00:00Z",
    evidencia: {
      cnpj: "12345678000190",
      doacao: 480000,
      ano_eleicao: 2024,
      contratos_pos: 38,
    },
    disclaimer:
      "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa.",
    metodologiaUrl: "/metodologia#doador-beneficiado",
  },
];
```

- [ ] **Step 4: mock/index.ts**

```typescript
export * from "./municipios";
export * from "./empresas";
export * from "./alertas";
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/lib/mock/
git commit -m "feat(web): mock data for development without database"
```

---

### Task 14: Componentes UI primitivos

**Files:**
- Create: `apps/web/lib/cn.ts`
- Create: `apps/web/components/ui/badge.tsx`
- Create: `apps/web/components/ui/button.tsx`
- Create: `apps/web/components/ui/card.tsx`
- Create: `apps/web/components/ui/input.tsx`

- [ ] **Step 1: lib/cn.ts**

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 2: components/ui/badge.tsx**

```tsx
import { cn } from "@/lib/cn";
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border",
  {
    variants: {
      variant: {
        default: "bg-bg-elevated border-border text-fg",
        fact: "bg-emerald-950/40 border-emerald-800/50 text-emerald-400",
        attention: "bg-amber-950/40 border-amber-800/50 text-amber-400",
        strong: "bg-red-950/40 border-red-800/50 text-red-400",
        muted: "bg-bg-subtle border-border-subtle text-fg-muted",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
```

- [ ] **Step 3: components/ui/button.tsx**

```tsx
import { cn } from "@/lib/cn";
import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef } from "react";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fg/40",
  {
    variants: {
      variant: {
        primary: "bg-fg text-bg hover:bg-fg/90",
        secondary: "bg-bg-elevated border border-border text-fg hover:bg-bg-subtle",
        ghost: "text-fg hover:bg-bg-elevated",
      },
      size: {
        sm: "h-8 px-3",
        md: "h-10 px-4",
        lg: "h-12 px-6 text-base",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  )
);
Button.displayName = "Button";
```

- [ ] **Step 4: components/ui/card.tsx**

```tsx
import { cn } from "@/lib/cn";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-bg-subtle p-4",
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-3", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-base font-semibold text-fg", className)} {...props} />;
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-sm text-fg-muted", className)} {...props} />;
}
```

- [ ] **Step 5: components/ui/input.tsx**

```tsx
import { cn } from "@/lib/cn";
import { forwardRef } from "react";

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-md border border-border bg-bg-elevated px-3 py-2 text-sm text-fg placeholder:text-fg-subtle focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fg/40",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
```

- [ ] **Step 6: Commit**

```bash
git add apps/web/lib/cn.ts apps/web/components/ui/
git commit -m "feat(web): UI primitives (badge, button, card, input)"
```

---

### Task 15: Componentes de layout

**Files:**
- Create: `apps/web/components/layout/header.tsx`
- Create: `apps/web/components/layout/footer.tsx`

- [ ] **Step 1: header.tsx**

```tsx
import Link from "next/link";
import { Eye } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-border-subtle">
      <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Eye className="size-5 text-fg" />
          <span className="font-semibold tracking-tight">Olho Público</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm text-fg-muted">
          <Link href="/busca" className="hover:text-fg">Busca</Link>
          <Link href="/metodologia" className="hover:text-fg">Metodologia</Link>
          <Link href="/contestar" className="hover:text-fg">Contestar dado</Link>
        </nav>
      </div>
    </header>
  );
}
```

- [ ] **Step 2: footer.tsx**

```tsx
import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border-subtle mt-16">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-fg-muted flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
        <div>
          <p className="text-fg font-medium">Olho Público</p>
          <p className="mt-1">
            Plataforma cívica baseada em dados oficiais. Sem opiniões — só fatos e sinais documentados.
          </p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link href="/metodologia" className="hover:text-fg">Metodologia</Link>
          <Link href="/privacidade" className="hover:text-fg">Privacidade</Link>
          <Link href="/contestar" className="hover:text-fg">Contestar dado</Link>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-fg">
            Código (GitHub)
          </a>
        </div>
      </div>
    </footer>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/web/components/layout/
git commit -m "feat(web): header and footer layout components"
```

---

### Task 16: Componente AlertCard

**Files:**
- Create: `apps/web/components/alerts/alert-card.tsx`

- [ ] **Step 1: alert-card.tsx**

```tsx
import Link from "next/link";
import type { AlertaDisplay } from "@olho/shared";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatDate } from "@olho/shared";

const severidadeLabel = {
  info: "Informativo",
  atencao: "Atenção",
  forte: "Sinal forte",
} as const;

const severidadeVariant = {
  info: "fact",
  atencao: "attention",
  forte: "strong",
} as const;

export function AlertCard({ alerta }: { alerta: AlertaDisplay }) {
  return (
    <Card className="border-l-4 border-l-accent-strong/0 data-[severidade=info]:border-l-accent-fact data-[severidade=atencao]:border-l-accent-attention data-[severidade=forte]:border-l-accent-strong"
          data-severidade={alerta.severidade}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <Badge variant={severidadeVariant[alerta.severidade]}>
          {severidadeLabel[alerta.severidade]}
        </Badge>
        <time className="text-xs text-fg-subtle">
          {formatDate(alerta.dataDeteccao)}
        </time>
      </div>
      <h4 className="font-semibold text-fg leading-snug mb-1">
        {alerta.tituloLegivel}
      </h4>
      <p className="text-sm text-fg-muted leading-relaxed">
        {alerta.resumoLegivel}
      </p>
      <div className="mt-3 pt-3 border-t border-border-subtle text-xs text-fg-subtle">
        <p className="italic mb-2">{alerta.disclaimer}</p>
        <Link href={alerta.metodologiaUrl} className="hover:text-fg underline-offset-2 hover:underline">
          Ver metodologia desta regra →
        </Link>
      </div>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/alerts/
git commit -m "feat(web): AlertCard with severity-based border"
```

---

### Task 17: Componentes de cidade — TopFornecedores e GastosPorArea

**Files:**
- Create: `apps/web/components/city/top-fornecedores.tsx`
- Create: `apps/web/components/city/gastos-por-area.tsx`
- Create: `apps/web/components/city/comparacao-similares.tsx`

- [ ] **Step 1: top-fornecedores.tsx**

```tsx
import Link from "next/link";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBRLCompact, formatCNPJ, type AlertaDisplay } from "@olho/shared";

interface TopFornecedor {
  cnpj: string;
  razaoSocial: string;
  totalContratos: number;
  valorTotal: string;
}

export function TopFornecedores({ items }: { items: TopFornecedor[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Maiores fornecedores</CardTitle>
      </CardHeader>
      <ul className="divide-y divide-border-subtle">
        {items.map((f) => (
          <li key={f.cnpj} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3">
            <div className="min-w-0">
              <Link
                href={`/empresa/${f.cnpj}`}
                className="font-medium text-fg hover:underline truncate block"
              >
                {f.razaoSocial}
              </Link>
              <p className="text-xs text-fg-subtle font-mono">{formatCNPJ(f.cnpj)}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="font-mono font-semibold text-fg">{formatBRLCompact(f.valorTotal)}</p>
              <p className="text-xs text-fg-subtle">{f.totalContratos} contratos</p>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
```

- [ ] **Step 2: gastos-por-area.tsx**

```tsx
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBRLCompact } from "@olho/shared";

interface GastoArea {
  area: string;
  valor: string;
  percentual: number;
}

export function GastosPorArea({ items }: { items: GastoArea[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Gastos por área</CardTitle>
      </CardHeader>
      <ul className="space-y-3">
        {items.map((g) => (
          <li key={g.area}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-fg">{g.area}</span>
              <span className="font-mono text-fg-muted">{formatBRLCompact(g.valor)}</span>
            </div>
            <div className="h-2 rounded-full bg-bg-elevated overflow-hidden">
              <div
                className="h-full bg-fg/80"
                style={{ width: `${g.percentual}%` }}
                aria-label={`${g.percentual}%`}
              />
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
```

- [ ] **Step 3: comparacao-similares.tsx**

```tsx
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

interface ComparacaoSimilar {
  municipioId: string;
  municipioNome: string;
  uf: string;
  metric: string;
  valorComparado: string;
}

export function ComparacaoSimilares({ items }: { items: ComparacaoSimilar[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Comparação com cidades similares</CardTitle>
        <CardDescription>
          Razão entre o gasto desta cidade e o gasto da cidade comparada (1.0 = igual).
        </CardDescription>
      </CardHeader>
      <ul className="divide-y divide-border-subtle">
        {items.map((c) => (
          <li key={c.municipioId} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between">
            <Link
              href={`/cidade/${c.uf}/${c.municipioId}`}
              className="text-fg hover:underline"
            >
              {c.municipioNome} <span className="text-fg-subtle">— {c.uf}</span>
            </Link>
            <span className="font-mono text-sm">{c.valorComparado}x</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add apps/web/components/city/
git commit -m "feat(web): city components (fornecedores, areas, comparacao)"
```

---

### Task 18: Componente SearchBar

**Files:**
- Create: `apps/web/components/search/search-bar.tsx`

- [ ] **Step 1: search-bar.tsx**

```tsx
"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export function SearchBar({ size = "lg" }: { size?: "md" | "lg" }) {
  const router = useRouter();
  const [q, setQ] = useState("");

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (q.trim()) router.push(`/busca?q=${encodeURIComponent(q.trim())}`);
  }

  const inputClass = size === "lg" ? "h-14 text-lg px-4" : "";

  return (
    <form onSubmit={onSubmit} className="flex gap-2 w-full max-w-2xl mx-auto">
      <Input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Digite sua cidade ou um CNPJ"
        className={inputClass}
        aria-label="Buscar cidade ou empresa"
      />
      <Button type="submit" size={size === "lg" ? "lg" : "md"}>
        <Search className="size-4 mr-2" /> Buscar
      </Button>
    </form>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/search/
git commit -m "feat(web): SearchBar with router push to /busca"
```

---

### Task 19: Página inicial (home)

**Files:**
- Create: `apps/web/app/(public)/layout.tsx`
- Create: `apps/web/app/(public)/page.tsx`

- [ ] **Step 1: layout.tsx (public)**

```tsx
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
```

- [ ] **Step 2: page.tsx (home)**

```tsx
import Link from "next/link";
import { SearchBar } from "@/components/search/search-bar";
import { AlertCard } from "@/components/alerts/alert-card";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { mockMunicipios, mockAlertasSP } from "@/lib/mock";

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="border-b border-border-subtle">
        <div className="mx-auto max-w-4xl px-4 py-20 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-fg leading-tight">
            Para onde vai o<br />
            <span className="text-fg/70">dinheiro público brasileiro?</span>
          </h1>
          <p className="mt-6 text-lg text-fg-muted max-w-2xl mx-auto">
            Olho Público mostra contratos, fornecedores e sinais de alerta da sua cidade
            usando apenas dados oficiais.
          </p>
          <div className="mt-10">
            <SearchBar size="lg" />
          </div>
        </div>
      </section>

      {/* Cidades em destaque */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-2xl font-semibold mb-6">Cidades em destaque</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {mockMunicipios.map((m) => (
            <Link key={m.idIbge} href={`/cidade/${m.uf}/${m.slug}`}>
              <Card className="h-full hover:border-fg/30 transition-colors">
                <CardHeader>
                  <CardTitle>{m.nome} <span className="text-fg-subtle text-sm font-normal">— {m.uf}</span></CardTitle>
                  <CardDescription>
                    {m.populacao?.toLocaleString("pt-BR")} habitantes
                  </CardDescription>
                </CardHeader>
                <p className="text-sm text-fg-muted">
                  Prefeito: <span className="text-fg">{m.prefeitoNome}</span> ({m.prefeitoPartido})
                </p>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Feed nacional de alertas (mock) */}
      <section className="mx-auto max-w-6xl px-4 py-16 border-t border-border-subtle">
        <div className="flex items-end justify-between mb-6">
          <h2 className="text-2xl font-semibold">Sinais recentes</h2>
          <p className="text-sm text-fg-subtle">Detectados automaticamente em dados oficiais</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockAlertasSP.map((a) => (
            <AlertCard key={a.id} alerta={a} />
          ))}
        </div>
      </section>
    </div>
  );
}
```

- [ ] **Step 3: Test no browser**

```bash
cd apps/web && pnpm dev
```

Abrir http://localhost:3000 — verificar:
- Hero com busca grande
- 3 cards de cidade
- 3 alert cards no feed

- [ ] **Step 4: Commit**

```bash
git add apps/web/app/
git commit -m "feat(web): home page with hero, cities and alerts feed"
```

---

### Task 20: Página da cidade (storytelling)

**Files:**
- Create: `apps/web/app/(public)/cidade/[uf]/[slug]/page.tsx`

- [ ] **Step 1: page.tsx**

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
import { formatBRLCompact, formatNumber } from "@olho/shared";
import { BarChart3 } from "lucide-react";

interface Props {
  params: Promise<{ uf: string; slug: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { uf, slug } = await params;
  const m = mockMunicipios.find((mu) => mu.uf === uf.toUpperCase() && mu.slug === slug);
  if (!m) return {};
  const ag = mockAgregacoes[m.idIbge];
  const total = ag ? formatBRLCompact(ag.totalContratosFederais) : "";
  return {
    title: `${m.nome} — ${m.uf}`,
    description: total
      ? `Em 2025, ${m.nome} (${m.uf}) recebeu ${total} em contratos federais. Veja sinais detectados e maiores fornecedores.`
      : `Dados públicos de ${m.nome}, ${m.uf}.`,
  };
}

export default async function CidadePage({ params }: Props) {
  const { uf, slug } = await params;
  const municipio = mockMunicipios.find((m) => m.uf === uf.toUpperCase() && m.slug === slug);
  if (!municipio) notFound();

  const agregacoes = mockAgregacoes[municipio.idIbge];
  const alertas = municipio.idIbge === "3550308" ? mockAlertasSP : [];

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      {/* Header da cidade */}
      <header className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <Link href="/" className="text-sm text-fg-subtle hover:text-fg">
            Início
          </Link>
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
          <Badge variant="muted">
            Cobertura prefeitura: {municipio.coberturaPrefeitura}
          </Badge>
          {municipio.erpDetectado && (
            <Badge variant="muted">ERP: {municipio.erpDetectado}</Badge>
          )}
          <Link href={`/cidade/${municipio.uf}/${municipio.slug}/dashboard`}>
            <Button variant="secondary" size="sm">
              <BarChart3 className="size-4 mr-2" /> Ver dashboard completo
            </Button>
          </Link>
        </div>
      </header>

      {/* KPIs do ano */}
      {agregacoes && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
          <KpiCard label="Contratos federais" value={formatBRLCompact(agregacoes.totalContratosFederais)} />
          <KpiCard label="Contratos prefeitura" value={formatBRLCompact(agregacoes.totalContratosPrefeitura)} />
          <KpiCard label="Total de contratos" value={formatNumber(agregacoes.qtdContratosFederais + agregacoes.qtdContratosPrefeitura)} />
          <KpiCard label="Sinais detectados" value={String(alertas.length)} highlight={alertas.length > 0} />
        </section>
      )}

      {/* Sinais (alertas) */}
      {alertas.length > 0 && (
        <section className="mb-10">
          <h2 className="text-xl font-semibold mb-4">Sinais detectados</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {alertas.map((a) => (
              <AlertCard key={a.id} alerta={a} />
            ))}
          </div>
        </section>
      )}

      {/* Top fornecedores + gastos por área */}
      {agregacoes && (
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-10">
          <TopFornecedores items={agregacoes.topFornecedores} />
          <GastosPorArea items={agregacoes.gastosPorArea} />
        </section>
      )}

      {/* Comparação */}
      {agregacoes && agregacoes.comparacaoSimilares.length > 0 && (
        <section className="mb-10">
          <ComparacaoSimilares items={agregacoes.comparacaoSimilares} />
        </section>
      )}

      {/* Estado vazio para cidades sem dados ainda */}
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

- [ ] **Step 2: Test no browser**

Abrir http://localhost:3000/cidade/SP/sao-paulo — verificar layout completo.

- [ ] **Step 3: Commit**

```bash
git add apps/web/app/\(public\)/cidade/
git commit -m "feat(web): page cidade with storytelling layout"
```

---

### Task 21: Página dashboard da cidade

**Files:**
- Create: `apps/web/app/(public)/cidade/[uf]/[slug]/dashboard/page.tsx`

- [ ] **Step 1: page.tsx**

```tsx
import { notFound } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { mockMunicipios, mockAgregacoes } from "@/lib/mock";
import { formatBRL, formatNumber } from "@olho/shared";
import { ArrowLeft } from "lucide-react";

interface Props {
  params: Promise<{ uf: string; slug: string }>;
}

export default async function DashboardCidade({ params }: Props) {
  const { uf, slug } = await params;
  const municipio = mockMunicipios.find((m) => m.uf === uf.toUpperCase() && m.slug === slug);
  if (!municipio) notFound();
  const ag = mockAgregacoes[municipio.idIbge];

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link href={`/cidade/${municipio.uf}/${municipio.slug}`} className="text-sm text-fg-subtle hover:text-fg flex items-center gap-1">
            <ArrowLeft className="size-3" /> Voltar para visão geral
          </Link>
          <h1 className="mt-2 text-3xl font-bold">{municipio.nome} — Dashboard</h1>
        </div>
      </div>

      {!ag && (
        <p className="text-fg-muted">Sem dados consolidados.</p>
      )}

      {ag && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card>
            <CardHeader><CardTitle>Total contratos federais</CardTitle></CardHeader>
            <p className="font-mono text-2xl">{formatBRL(ag.totalContratosFederais)}</p>
            <p className="text-sm text-fg-muted mt-1">{formatNumber(ag.qtdContratosFederais)} contratos</p>
          </Card>
          <Card>
            <CardHeader><CardTitle>Total contratos prefeitura</CardTitle></CardHeader>
            <p className="font-mono text-2xl">{formatBRL(ag.totalContratosPrefeitura)}</p>
            <p className="text-sm text-fg-muted mt-1">{formatNumber(ag.qtdContratosPrefeitura)} contratos</p>
          </Card>
          <Card>
            <CardHeader><CardTitle>População</CardTitle></CardHeader>
            <p className="font-mono text-2xl">{formatNumber(municipio.populacao ?? 0)}</p>
          </Card>
          <Card className="md:col-span-2 lg:col-span-3">
            <CardHeader><CardTitle>Top 10 fornecedores</CardTitle></CardHeader>
            <table className="w-full text-sm">
              <thead className="text-fg-subtle text-xs uppercase tracking-wider">
                <tr>
                  <th className="text-left pb-2">Empresa</th>
                  <th className="text-left pb-2">CNPJ</th>
                  <th className="text-right pb-2">Contratos</th>
                  <th className="text-right pb-2">Valor total</th>
                </tr>
              </thead>
              <tbody>
                {ag.topFornecedores.map((f) => (
                  <tr key={f.cnpj} className="border-t border-border-subtle">
                    <td className="py-2">
                      <Link href={`/empresa/${f.cnpj}`} className="hover:underline">{f.razaoSocial}</Link>
                    </td>
                    <td className="py-2 font-mono text-fg-muted">{f.cnpj}</td>
                    <td className="py-2 text-right font-mono">{f.totalContratos}</td>
                    <td className="py-2 text-right font-mono">{formatBRL(f.valorTotal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/app/\(public\)/cidade/
git commit -m "feat(web): page dashboard da cidade with KPIs e top fornecedores"
```

---

### Task 22: Página da empresa (V1 leve)

**Files:**
- Create: `apps/web/app/(public)/empresa/[cnpj]/page.tsx`

- [ ] **Step 1: page.tsx**

```tsx
import { notFound } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { mockEmpresas } from "@/lib/mock";
import { formatCNPJ, formatDate } from "@olho/shared";

interface Props {
  params: Promise<{ cnpj: string }>;
}

export default async function EmpresaPage({ params }: Props) {
  const { cnpj } = await params;
  const cleanCnpj = cnpj.replace(/\D/g, "");
  const empresa = mockEmpresas.find((e) => e.cnpj === cleanCnpj);
  if (!empresa) notFound();

  const flagsAtivas = Object.entries(empresa.flags).filter(([, v]) => v);

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <header className="mb-8">
        <p className="text-sm text-fg-subtle font-mono">{formatCNPJ(empresa.cnpj)}</p>
        <h1 className="mt-1 text-3xl font-bold">{empresa.razaoSocial}</h1>
        {empresa.nomeFantasia && <p className="text-fg-muted">{empresa.nomeFantasia}</p>}
        <div className="mt-3 flex flex-wrap gap-2">
          {empresa.situacao && <Badge variant="muted">{empresa.situacao}</Badge>}
          {flagsAtivas.map(([k]) => (
            <Badge key={k} variant={k === "sancionada" ? "strong" : k === "foguete" ? "attention" : "fact"}>
              {k}
            </Badge>
          ))}
        </div>
      </header>

      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Dados cadastrais</CardTitle>
          <CardDescription>Fonte: Receita Federal</CardDescription>
        </CardHeader>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div><dt className="text-fg-subtle">Abertura</dt><dd className="text-fg">{empresa.dataAbertura ? formatDate(empresa.dataAbertura) : "—"}</dd></div>
          <div><dt className="text-fg-subtle">CNAE principal</dt><dd className="text-fg font-mono">{empresa.cnaePrincipal ?? "—"}</dd></div>
          <div><dt className="text-fg-subtle">Sede</dt><dd className="text-fg">{empresa.municipioSedeId ?? "—"}</dd></div>
        </dl>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Contratos públicos, sanções, doações</CardTitle>
          <CardDescription>
            Esta seção é populada após a ingestão dos dados (V2). Por ora, exibimos apenas o cadastro.
          </CardDescription>
        </CardHeader>
        <div className="text-sm text-fg-muted">
          <p>Volte em breve. Veja a <Link href="/metodologia" className="underline">metodologia</Link> para entender as fontes.</p>
        </div>
      </Card>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/app/\(public\)/empresa/
git commit -m "feat(web): empresa page V1 (cadastro mock)"
```

---

### Task 23: Páginas estáticas — busca, metodologia, contestar, privacidade

**Files:**
- Create: `apps/web/app/(public)/busca/page.tsx`
- Create: `apps/web/app/(public)/metodologia/page.tsx`
- Create: `apps/web/app/(public)/contestar/page.tsx`
- Create: `apps/web/app/(public)/privacidade/page.tsx`

- [ ] **Step 1: busca/page.tsx**

```tsx
import { mockMunicipios, mockEmpresas } from "@/lib/mock";
import Link from "next/link";
import { SearchBar } from "@/components/search/search-bar";
import { formatCNPJ } from "@olho/shared";

interface Props {
  searchParams: Promise<{ q?: string }>;
}

export default async function BuscaPage({ searchParams }: Props) {
  const { q = "" } = await searchParams;
  const term = q.toLowerCase().trim();

  const cidades = term
    ? mockMunicipios.filter(
        (m) => m.nome.toLowerCase().includes(term) || m.slug.includes(term)
      )
    : [];

  const cleanQ = term.replace(/\D/g, "");
  const empresas = cleanQ.length >= 8
    ? mockEmpresas.filter((e) => e.cnpj.includes(cleanQ) || e.razaoSocial.toLowerCase().includes(term))
    : [];

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold mb-6">Busca</h1>
      <SearchBar />
      {term && (
        <div className="mt-8">
          {cidades.length === 0 && empresas.length === 0 && (
            <p className="text-fg-muted">Nenhum resultado para &ldquo;{q}&rdquo;.</p>
          )}
          {cidades.length > 0 && (
            <section className="mb-6">
              <h2 className="text-sm uppercase tracking-wider text-fg-subtle mb-2">Cidades</h2>
              <ul className="space-y-2">
                {cidades.map((c) => (
                  <li key={c.idIbge}>
                    <Link href={`/cidade/${c.uf}/${c.slug}`} className="text-fg hover:underline">
                      {c.nome} <span className="text-fg-subtle">— {c.uf}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
          {empresas.length > 0 && (
            <section>
              <h2 className="text-sm uppercase tracking-wider text-fg-subtle mb-2">Empresas</h2>
              <ul className="space-y-2">
                {empresas.map((e) => (
                  <li key={e.cnpj}>
                    <Link href={`/empresa/${e.cnpj}`} className="text-fg hover:underline">
                      {e.razaoSocial}
                    </Link>{" "}
                    <span className="text-xs text-fg-subtle font-mono">{formatCNPJ(e.cnpj)}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: metodologia/page.tsx**

```tsx
import Link from "next/link";

export const metadata = { title: "Metodologia" };

export default function MetodologiaPage() {
  return (
    <article className="mx-auto max-w-3xl px-4 py-12 prose prose-invert">
      <h1>Metodologia</h1>

      <h2>Princípios</h2>
      <ul>
        <li><strong>Fato antes de opinião</strong> — só dados oficiais agregados.</li>
        <li><strong>Sinais não são acusações</strong> — alertas levam disclaimer e link para evidência.</li>
        <li><strong>Cobertura nacional</strong> — qualquer das 5.570 cidades pode ser consultada.</li>
        <li><strong>Transparência</strong> — toda regra é versionada em código aberto.</li>
      </ul>

      <h2>Fontes</h2>
      <ul>
        <li><strong>Portal da Transparência (CGU)</strong> — contratos, convênios, transferências federais.</li>
        <li><strong>Receita Federal</strong> — base CNPJ (empresas e sócios).</li>
        <li><strong>CEIS / CNEP (CGU)</strong> — empresas inidôneas e sancionadas.</li>
        <li><strong>TSE</strong> — doações eleitorais.</li>
        <li><strong>Compras.gov.br</strong> — licitações federais.</li>
        <li><strong>IBGE</strong> — municípios, população, IDH.</li>
        <li><strong>Portais municipais (via ERPs)</strong> — contratos e licitações de prefeituras.</li>
      </ul>

      <h2>Regras de alerta</h2>
      <p>Cada regra tem um identificador, parâmetros documentados e disclaimer obrigatório.</p>
      <h3 id="empresa-foguete">EMPRESA_FOGUETE</h3>
      <p>CNPJ aberto há &lt;12 meses recebeu contrato &gt; R$ 500 mil. <em>Severidade padrão: forte.</em></p>
      <h3 id="dispensa-suspeita">DISPENSA_SUSPEITA</h3>
      <p>Contrato sem licitação acima de R$ 1 milhão. <em>Severidade padrão: atenção.</em></p>
      <h3 id="socio-sancionado">SOCIO_SANCIONADO</h3>
      <p>Empresa com contrato cujo sócio aparece em CEIS/CNEP. <em>Severidade padrão: forte.</em></p>
      <h3 id="crescimento-anomalo">CRESCIMENTO_ANOMALO</h3>
      <p>Empresa cujo faturamento público cresceu &gt;300% ano a ano. <em>Severidade padrão: atenção.</em></p>
      <h3 id="concentracao">CONCENTRACAO</h3>
      <p>Mesma empresa = &gt;40% dos contratos de uma secretaria. <em>Severidade padrão: informativo.</em></p>
      <h3 id="doador-beneficiado">DOADOR_BENEFICIADO</h3>
      <p>Empresa que doou para campanha do prefeito atual recebeu contrato após eleição. <em>Severidade padrão: atenção.</em></p>

      <h2>Direito de resposta</h2>
      <p>
        Encontrou um dado que considera incorreto ou descontextualizado?
        Use a <Link href="/contestar">página de contestação</Link>. Toda contestação procedente é
        publicada vinculada ao registro original.
      </p>

      <h2>Código aberto e auditabilidade</h2>
      <p>O código-fonte e todas as regras são públicos sob licença source-available.</p>
    </article>
  );
}
```

- [ ] **Step 3: contestar/page.tsx**

```tsx
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export const metadata = { title: "Contestar dado" };

export default function ContestarPage() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-3xl font-bold mb-2">Contestar dado</h1>
      <p className="text-fg-muted mb-8">
        Encontrou um dado que considera incorreto ou descontextualizado? Conte para a gente.
        Após análise, a resposta fica vinculada ao registro original.
      </p>

      <Card>
        <CardHeader>
          <CardTitle>Formulário</CardTitle>
          <CardDescription>
            Sua mensagem entra em fila de moderação. Em V1 ainda não há envio automático — utilize o email abaixo.
          </CardDescription>
        </CardHeader>
        <form className="space-y-4">
          <div>
            <label className="block text-sm text-fg-muted mb-1">Seu email</label>
            <Input type="email" placeholder="voce@exemplo.com" />
          </div>
          <div>
            <label className="block text-sm text-fg-muted mb-1">Link da página contestada</label>
            <Input type="url" placeholder="https://olhopublico.org/cidade/..." />
          </div>
          <div>
            <label className="block text-sm text-fg-muted mb-1">Mensagem</label>
            <textarea
              className="w-full rounded-md border border-border bg-bg-elevated px-3 py-2 text-sm text-fg min-h-32"
              placeholder="Descreva o que parece incorreto e, se possível, indique a fonte oficial divergente."
            />
          </div>
          <Button type="button" disabled>
            Enviar (em construção)
          </Button>
        </form>
        <p className="mt-4 text-sm text-fg-subtle">
          Por ora, envie para <a className="underline" href="mailto:contato@olhopublico.org">contato@olhopublico.org</a>.
        </p>
      </Card>
    </div>
  );
}
```

- [ ] **Step 4: privacidade/page.tsx**

```tsx
export const metadata = { title: "Política de privacidade" };

export default function PrivacidadePage() {
  return (
    <article className="mx-auto max-w-3xl px-4 py-12 prose prose-invert">
      <h1>Política de privacidade</h1>
      <p>Última atualização: 22/04/2026.</p>

      <h2>Resumo</h2>
      <ul>
        <li>O Olho Público <strong>não exige cadastro</strong> para navegação.</li>
        <li>Não usamos cookies de tracking nem identificadores publicitários.</li>
        <li>Analytics privacy-first: contagem agregada de visitas, sem identificação pessoal.</li>
        <li>Dados pessoais coletados: apenas email, opcional, em formulários de contestação.</li>
      </ul>

      <h2>Dados sobre terceiros</h2>
      <p>
        Exibimos dados públicos oficiais brasileiros (LAI — Lei 12.527/2011). CPFs aparecem
        sempre mascarados (ex: <code>***.123.456-**</code>) quando vinculados a doações ou sociedades.
        Razão social e dados cadastrais de empresas vêm da Receita Federal.
      </p>

      <h2>Direitos do titular (LGPD)</h2>
      <p>
        Para qualquer solicitação relacionada a dados pessoais, escreva para{" "}
        <a href="mailto:lgpd@olhopublico.org">lgpd@olhopublico.org</a>.
      </p>
    </article>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/\(public\)/
git commit -m "feat(web): páginas busca, metodologia, contestar e privacidade"
```

---

### Task 24: Sitemap e robots

**Files:**
- Create: `apps/web/app/sitemap.ts`
- Create: `apps/web/app/robots.ts`

- [ ] **Step 1: sitemap.ts**

```typescript
import type { MetadataRoute } from "next";
import { mockMunicipios } from "@/lib/mock";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

  const cityUrls = mockMunicipios.map((m) => ({
    url: `${base}/cidade/${m.uf}/${m.slug}`,
    lastModified: new Date(),
    changeFrequency: "daily" as const,
    priority: 0.8,
  }));

  return [
    { url: base, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
    { url: `${base}/metodologia`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.5 },
    { url: `${base}/privacidade`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    ...cityUrls,
  ];
}
```

- [ ] **Step 2: robots.ts**

```typescript
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
  return {
    rules: [{ userAgent: "*", allow: "/" }],
    sitemap: `${base}/sitemap.xml`,
  };
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/web/app/sitemap.ts apps/web/app/robots.ts
git commit -m "feat(web): sitemap.xml e robots.txt"
```

---

## Fase 1.5 — App `apps/etl` (Python)

### Task 25: Bootstrap projeto Python

**Files:**
- Create: `apps/etl/pyproject.toml`
- Create: `apps/etl/Dockerfile`
- Create: `apps/etl/.python-version`
- Create: `apps/etl/README.md`

- [ ] **Step 1: pyproject.toml**

```toml
[project]
name = "olho-publico-etl"
version = "0.1.0"
description = "ETL pipelines for Olho Público — Brazilian public data"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "duckdb>=1.1.0",
    "polars>=1.12.0",
    "psycopg[binary,pool]>=3.2.0",
    "playwright>=1.48.0",
    "boto3>=1.35.0",
    "brutils>=2.2.0",
    "python-stdnum>=1.20",
    "structlog>=24.4.0",
    "tenacity>=9.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.7.0",
    "mypy>=1.13.0",
    "respx>=0.21.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["olho_publico_etl"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "C4", "SIM"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: .python-version**

```
3.12
```

- [ ] **Step 3: Dockerfile**

```dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

COPY . .

RUN playwright install --with-deps chromium

CMD ["python", "-m", "olho_publico_etl"]
```

- [ ] **Step 4: README.md**

```markdown
# Olho Público — ETL

Pipelines de ingestão das fontes oficiais brasileiras.

## Setup local

```bash
cd apps/etl
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

## Rodar testes

```bash
pytest -v
```
```

- [ ] **Step 5: Commit**

```bash
git add apps/etl/
git commit -m "chore(etl): python project bootstrap with pyproject and Dockerfile"
```

---

### Task 26: Config + utils

**Files:**
- Create: `apps/etl/olho_publico_etl/__init__.py`
- Create: `apps/etl/olho_publico_etl/config.py`
- Create: `apps/etl/olho_publico_etl/utils/__init__.py`
- Create: `apps/etl/olho_publico_etl/utils/cpf_mask.py`
- Create: `apps/etl/olho_publico_etl/utils/slug.py`

- [ ] **Step 1: __init__.py (vazio)**

- [ ] **Step 2: config.py**

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

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 3: utils/cpf_mask.py**

```python
def mask_cpf(cpf: str | None) -> str | None:
    """Return CPF in masked format like '***.123.456-**'.

    Accepts CPF with or without punctuation. Returns None if input is empty or invalid.
    """
    if not cpf:
        return None
    digits = "".join(ch for ch in cpf if ch.isdigit())
    if len(digits) != 11:
        return None
    return f"***.{digits[3:6]}.{digits[6:9]}-**"
```

- [ ] **Step 4: utils/slug.py**

```python
import unicodedata
import re


def slugify(value: str) -> str:
    """Lowercased, accent-free, dashed slug."""
    nfkd = unicodedata.normalize("NFD", value)
    no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", no_accents).strip("-").lower()
    return cleaned
```

- [ ] **Step 5: Test**

Create `apps/etl/tests/unit/test_utils.py`:

```python
from olho_publico_etl.utils.cpf_mask import mask_cpf
from olho_publico_etl.utils.slug import slugify


def test_mask_cpf_with_punctuation():
    assert mask_cpf("123.456.789-09") == "***.456.789-**"


def test_mask_cpf_bare_digits():
    assert mask_cpf("12345678909") == "***.456.789-**"


def test_mask_cpf_invalid_returns_none():
    assert mask_cpf("123") is None
    assert mask_cpf("") is None
    assert mask_cpf(None) is None


def test_slugify_accents():
    assert slugify("São Paulo") == "sao-paulo"


def test_slugify_complex():
    assert slugify("Itabaiana - SE") == "itabaiana-se"
```

- [ ] **Step 6: Run tests**

```bash
cd apps/etl && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

Expected: 5 tests pass.

- [ ] **Step 7: Commit**

```bash
git add apps/etl/
git commit -m "feat(etl): config, cpf_mask and slugify utils with tests"
```

---

### Task 27: Pydantic models

**Files:**
- Create: `apps/etl/olho_publico_etl/models/__init__.py`
- Create: `apps/etl/olho_publico_etl/models/municipio.py`
- Create: `apps/etl/olho_publico_etl/models/empresa.py`
- Create: `apps/etl/olho_publico_etl/models/contrato.py`
- Create: `apps/etl/olho_publico_etl/models/sancao.py`
- Create: `apps/etl/olho_publico_etl/models/doacao.py`
- Create: `apps/etl/olho_publico_etl/models/alerta.py`

- [ ] **Step 1: models/__init__.py (barrel)**

```python
from .municipio import Municipio
from .empresa import Empresa, Socio
from .contrato import Contrato, FonteContrato
from .sancao import Sancao
from .doacao import Doacao
from .alerta import Alerta, SeveridadeAlerta

__all__ = [
    "Municipio",
    "Empresa", "Socio",
    "Contrato", "FonteContrato",
    "Sancao",
    "Doacao",
    "Alerta", "SeveridadeAlerta",
]
```

- [ ] **Step 2: models/municipio.py**

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


CoberturaPrefeitura = Literal["nenhuma", "parcial", "completa"]


class Municipio(BaseModel):
    id_ibge: str = Field(min_length=7, max_length=7)
    nome: str
    slug: str
    uf: str = Field(min_length=2, max_length=2)
    populacao: int | None = None
    idh: float | None = None
    geometria: str | None = None
    prefeito_nome: str | None = None
    prefeito_partido: str | None = None
    cobertura_prefeitura: CoberturaPrefeitura = "nenhuma"
    erp_detectado: str | None = None
    atualizado_em: datetime = Field(default_factory=datetime.utcnow)
```

- [ ] **Step 3: models/empresa.py**

```python
from datetime import date, datetime
from pydantic import BaseModel, Field


class Empresa(BaseModel):
    cnpj: str = Field(min_length=14, max_length=14, pattern=r"^\d{14}$")
    razao_social: str
    nome_fantasia: str | None = None
    data_abertura: date | None = None
    situacao: str | None = None
    cnae_principal: str | None = None
    municipio_sede_id: str | None = None
    flags: dict[str, bool] = Field(default_factory=dict)
    atualizado_em: datetime = Field(default_factory=datetime.utcnow)


class Socio(BaseModel):
    cnpj: str = Field(min_length=14, max_length=14)
    cpf_mascarado: str | None = None
    nome: str
    tipo: str | None = None
    data_entrada: date | None = None
```

- [ ] **Step 4: models/contrato.py**

```python
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel


FonteContrato = Literal[
    "portal_transparencia",
    "compras_gov",
    "prefeitura_el",
    "prefeitura_ipm",
    "prefeitura_betha",
    "prefeitura_equiplano",
]


class Contrato(BaseModel):
    municipio_aplicacao_id: str | None = None
    cnpj_fornecedor: str | None = None
    orgao_contratante: str
    objeto: str
    valor: Decimal
    data_assinatura: date
    modalidade_licitacao: str | None = None
    fonte: FonteContrato
    dados_originais_url: str | None = None
```

- [ ] **Step 5: models/sancao.py**

```python
from datetime import date
from pydantic import BaseModel


class Sancao(BaseModel):
    cnpj: str
    tipo_sancao: str
    orgao_sancionador: str
    data_inicio: date
    data_fim: date | None = None
    motivo: str | None = None
    fonte_url: str | None = None
```

- [ ] **Step 6: models/doacao.py**

```python
from decimal import Decimal
from pydantic import BaseModel


class Doacao(BaseModel):
    cnpj_doador: str | None = None
    cpf_doador_mascarado: str | None = None
    candidato_nome: str
    candidato_cargo: str
    partido: str | None = None
    valor: Decimal
    ano_eleicao: int
    municipio_id: str | None = None
```

- [ ] **Step 7: models/alerta.py**

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


SeveridadeAlerta = Literal["info", "atencao", "forte"]


class Alerta(BaseModel):
    tipo: str
    severidade: SeveridadeAlerta
    municipio_id: str | None = None
    cnpj_envolvido: str | None = None
    evidencia: dict
    data_deteccao: datetime = Field(default_factory=datetime.utcnow)
    regra_versao: str
```

- [ ] **Step 8: Test models**

Create `apps/etl/tests/unit/test_models.py`:

```python
from datetime import date
from decimal import Decimal
import pytest
from pydantic import ValidationError
from olho_publico_etl.models import Empresa, Contrato, Alerta


def test_empresa_valida():
    e = Empresa(cnpj="12345678000190", razao_social="Teste S.A.")
    assert e.cnpj == "12345678000190"
    assert e.flags == {}


def test_empresa_cnpj_invalido_falha():
    with pytest.raises(ValidationError):
        Empresa(cnpj="123", razao_social="X")


def test_contrato_valida():
    c = Contrato(
        orgao_contratante="Prefeitura X",
        objeto="Pavimentação",
        valor=Decimal("12000000.00"),
        data_assinatura=date(2025, 6, 1),
        fonte="portal_transparencia",
    )
    assert c.valor == Decimal("12000000.00")


def test_alerta_severidade_validada():
    with pytest.raises(ValidationError):
        Alerta(tipo="X", severidade="invalido", evidencia={}, regra_versao="1.0.0")
```

- [ ] **Step 9: Run tests**

```bash
pytest -v
```

Expected: 4 new tests pass.

- [ ] **Step 10: Commit**

```bash
git add apps/etl/
git commit -m "feat(etl): pydantic models for all domain entities with tests"
```

---

### Task 28: Source ABC + esqueletos de fontes

**Files:**
- Create: `apps/etl/olho_publico_etl/sources/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/base.py`
- Create: `apps/etl/olho_publico_etl/sources/transparencia/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/transparencia/client.py`
- Create: `apps/etl/olho_publico_etl/sources/receita/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/receita/downloader.py`
- Create: `apps/etl/olho_publico_etl/sources/ceis_cnep/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/tse/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/compras/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/ibge/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/prefeituras/__init__.py`
- Create: `apps/etl/olho_publico_etl/sources/prefeituras/base.py`

- [ ] **Step 1: sources/base.py**

```python
from abc import ABC, abstractmethod
from typing import Iterator
from pydantic import BaseModel


class Source(ABC):
    """Base class for all data sources.

    Each source knows how to:
    - Download / fetch its raw data
    - Yield validated Pydantic records
    """

    name: str

    @abstractmethod
    def fetch(self) -> Iterator[BaseModel]:
        """Yield validated records from this source."""
```

- [ ] **Step 2: sources/transparencia/client.py (skeleton)**

```python
"""Portal da Transparência (CGU) — placeholder client.

Real implementation in plan P2. This file pins the structure.
"""
from typing import Iterator
from olho_publico_etl.models import Contrato
from olho_publico_etl.sources.base import Source


class TransparenciaSource(Source):
    name = "portal_transparencia"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch(self) -> Iterator[Contrato]:
        raise NotImplementedError("Implementado no plano P2 — exige chave de API CGU")
```

- [ ] **Step 3: sources/receita/downloader.py (skeleton)**

```python
"""Receita Federal CNPJ base — placeholder downloader.

Real implementation in plan P3.
"""
from typing import Iterator
from olho_publico_etl.models import Empresa, Socio
from olho_publico_etl.sources.base import Source


class ReceitaCnpjSource(Source):
    name = "receita_cnpj"

    def fetch(self) -> Iterator[Empresa | Socio]:
        raise NotImplementedError("Implementado no plano P3 — exige download de 45 GB")
```

- [ ] **Step 4: sources/ceis_cnep/__init__.py (skeleton)**

```python
"""CEIS / CNEP — sanções CGU."""
```

- [ ] **Step 5: sources/tse/__init__.py (skeleton)**

```python
"""TSE — doações eleitorais."""
```

- [ ] **Step 6: sources/compras/__init__.py (skeleton)**

```python
"""Compras.gov.br — licitações federais."""
```

- [ ] **Step 7: sources/ibge/__init__.py (skeleton)**

```python
"""IBGE — municípios, população e IDH."""
```

- [ ] **Step 8: sources/prefeituras/base.py**

```python
"""Base for ERP-based municipal scrapers.

Each subclass implements one ERP (E&L, IPM, Betha, Equiplano).
"""
from abc import abstractmethod
from typing import Iterator
from olho_publico_etl.models import Contrato
from olho_publico_etl.sources.base import Source


class PrefeituraErpSource(Source):
    erp_code: str

    def __init__(self, municipio_id: str, base_url: str):
        self.municipio_id = municipio_id
        self.base_url = base_url

    @abstractmethod
    def fetch(self) -> Iterator[Contrato]:
        """Implementação por ERP."""
```

- [ ] **Step 9: ERPs vazios para estrutura**

```bash
mkdir -p apps/etl/olho_publico_etl/sources/prefeituras/{el,ipm,betha,equiplano}
touch apps/etl/olho_publico_etl/sources/prefeituras/{el,ipm,betha,equiplano}/__init__.py
```

- [ ] **Step 10: Commit**

```bash
git add apps/etl/
git commit -m "feat(etl): source ABC and skeleton modules per fonte (real impl P2-P7)"
```

---

### Task 29: Engine de alertas (esqueleto + 1 regra de exemplo)

**Files:**
- Create: `apps/etl/olho_publico_etl/alerts/__init__.py`
- Create: `apps/etl/olho_publico_etl/alerts/engine.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/__init__.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/base.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/empresa_foguete.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/dispensa_suspeita.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/socio_sancionado.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/crescimento_anomalo.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/concentracao.py`
- Create: `apps/etl/olho_publico_etl/alerts/rules/doador_beneficiado.py`

- [ ] **Step 1: alerts/rules/base.py**

```python
from abc import ABC, abstractmethod
from typing import Iterator
from olho_publico_etl.models import Alerta


class RegraAlerta(ABC):
    """Base for alert detection rules.

    Each rule has a stable code, current semver version, and parameters.
    A rule reads from the database and yields Alerta records.
    """

    codigo: str
    versao_atual: str
    nome: str
    descricao: str
    severidade_padrao: str  # "info" | "atencao" | "forte"
    disclaimer: str = (
        "Este é um sinal automatizado baseado em dados públicos oficiais. "
        "Não constitui acusação ou conclusão investigativa."
    )

    @abstractmethod
    def detectar(self, conn) -> Iterator[Alerta]:
        """Run the rule against the database (psycopg connection) and yield alerts."""
```

- [ ] **Step 2: alerts/rules/empresa_foguete.py (regra completa de exemplo)**

```python
"""EMPRESA_FOGUETE: CNPJ aberto há <12 meses recebeu contrato > R$ 500k."""
from typing import Iterator
from olho_publico_etl.models import Alerta
from .base import RegraAlerta


class EmpresaFogueteRule(RegraAlerta):
    codigo = "EMPRESA_FOGUETE"
    versao_atual = "1.0.0"
    nome = "Empresa-foguete"
    descricao = (
        "Detecta empresas abertas há menos de 12 meses que receberam contratos "
        "públicos relevantes."
    )
    severidade_padrao = "forte"
    valor_minimo_brl = 500_000
    meses_maximos = 12

    def detectar(self, conn) -> Iterator[Alerta]:
        sql = """
        SELECT
            c.id AS contrato_id,
            c.cnpj_fornecedor,
            c.municipio_aplicacao_id,
            c.valor,
            c.data_assinatura,
            c.modalidade_licitacao,
            e.data_abertura
        FROM contratos c
        JOIN empresas e ON e.cnpj = c.cnpj_fornecedor
        WHERE e.data_abertura IS NOT NULL
          AND c.valor >= %s
          AND c.data_assinatura - e.data_abertura < INTERVAL '%s months';
        """
        with conn.cursor() as cur:
            cur.execute(sql, (self.valor_minimo_brl, self.meses_maximos))
            for row in cur:
                contrato_id, cnpj, municipio_id, valor, data_ass, modalidade, data_abertura = row
                yield Alerta(
                    tipo=self.codigo,
                    severidade=self.severidade_padrao,
                    municipio_id=municipio_id,
                    cnpj_envolvido=cnpj,
                    evidencia={
                        "contrato_id": contrato_id,
                        "valor": str(valor),
                        "data_assinatura": data_ass.isoformat(),
                        "data_abertura": data_abertura.isoformat(),
                        "modalidade": modalidade,
                    },
                    regra_versao=self.versao_atual,
                )
```

- [ ] **Step 3: rules/dispensa_suspeita.py (skeleton)**

```python
"""DISPENSA_SUSPEITA: contrato sem licitação acima de R$ 1M."""
from typing import Iterator
from olho_publico_etl.models import Alerta
from .base import RegraAlerta


class DispensaSuspeitaRule(RegraAlerta):
    codigo = "DISPENSA_SUSPEITA"
    versao_atual = "1.0.0"
    nome = "Dispensa de licitação relevante"
    descricao = "Detecta contratos sem licitação (modalidade DISPENSA) acima de limiar."
    severidade_padrao = "atencao"
    valor_minimo_brl = 1_000_000

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6 (engine completo)")
```

- [ ] **Step 4: outras regras (skeleton)**

`socio_sancionado.py`:
```python
"""SOCIO_SANCIONADO: empresa cujo sócio aparece em CEIS/CNEP."""
from typing import Iterator
from olho_publico_etl.models import Alerta
from .base import RegraAlerta


class SocioSancionadoRule(RegraAlerta):
    codigo = "SOCIO_SANCIONADO"
    versao_atual = "1.0.0"
    nome = "Sócio em lista de sanções"
    descricao = "Detecta contratos firmados com empresas cujo sócio aparece em CEIS/CNEP."
    severidade_padrao = "forte"

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
```

`crescimento_anomalo.py`:
```python
"""CRESCIMENTO_ANOMALO: empresa cujo faturamento público cresceu >300% ano a ano."""
from typing import Iterator
from olho_publico_etl.models import Alerta
from .base import RegraAlerta


class CrescimentoAnomaloRule(RegraAlerta):
    codigo = "CRESCIMENTO_ANOMALO"
    versao_atual = "1.0.0"
    nome = "Crescimento anômalo em receita pública"
    descricao = "Detecta empresas cuja receita pública cresceu mais de 300% ano a ano."
    severidade_padrao = "atencao"
    multiplicador_minimo = 4.0  # >300% = >=4x

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
```

`concentracao.py`:
```python
"""CONCENTRACAO: mesma empresa = >40% dos contratos de uma secretaria."""
from typing import Iterator
from olho_publico_etl.models import Alerta
from .base import RegraAlerta


class ConcentracaoRule(RegraAlerta):
    codigo = "CONCENTRACAO"
    versao_atual = "1.0.0"
    nome = "Concentração de fornecedor"
    descricao = "Detecta concentração excessiva de uma única empresa em um órgão."
    severidade_padrao = "info"
    percentual_minimo = 0.40

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
```

`doador_beneficiado.py`:
```python
"""DOADOR_BENEFICIADO: empresa que doou para campanha do prefeito recebeu contrato após eleição."""
from typing import Iterator
from olho_publico_etl.models import Alerta
from .base import RegraAlerta


class DoadorBeneficiadoRule(RegraAlerta):
    codigo = "DOADOR_BENEFICIADO"
    versao_atual = "1.0.0"
    nome = "Doador da campanha do prefeito"
    descricao = (
        "Detecta empresas doadoras da campanha vitoriosa para prefeito que receberam "
        "contratos após o início do mandato."
    )
    severidade_padrao = "atencao"

    def detectar(self, conn) -> Iterator[Alerta]:
        raise NotImplementedError("Implementação plena em plano P6")
```

- [ ] **Step 5: rules/__init__.py**

```python
from .empresa_foguete import EmpresaFogueteRule
from .dispensa_suspeita import DispensaSuspeitaRule
from .socio_sancionado import SocioSancionadoRule
from .crescimento_anomalo import CrescimentoAnomaloRule
from .concentracao import ConcentracaoRule
from .doador_beneficiado import DoadorBeneficiadoRule

ALL_RULES = [
    EmpresaFogueteRule(),
    DispensaSuspeitaRule(),
    SocioSancionadoRule(),
    CrescimentoAnomaloRule(),
    ConcentracaoRule(),
    DoadorBeneficiadoRule(),
]
```

- [ ] **Step 6: alerts/engine.py**

```python
"""Alert engine — runs all rules and persists alerts into Postgres."""
from typing import Iterator
from olho_publico_etl.models import Alerta
from .rules import ALL_RULES


def run_all_rules(conn) -> Iterator[Alerta]:
    """Run every rule against the DB and yield each alert produced."""
    for rule in ALL_RULES:
        try:
            yield from rule.detectar(conn)
        except NotImplementedError:
            continue
```

- [ ] **Step 7: Test that EmpresaFogueteRule has the right shape**

Create `apps/etl/tests/unit/test_alerts.py`:

```python
from olho_publico_etl.alerts.rules import (
    EmpresaFogueteRule, DispensaSuspeitaRule, SocioSancionadoRule,
    CrescimentoAnomaloRule, ConcentracaoRule, DoadorBeneficiadoRule, ALL_RULES,
)


def test_all_rules_present():
    codigos = {r.codigo for r in ALL_RULES}
    assert codigos == {
        "EMPRESA_FOGUETE", "DISPENSA_SUSPEITA", "SOCIO_SANCIONADO",
        "CRESCIMENTO_ANOMALO", "CONCENTRACAO", "DOADOR_BENEFICIADO",
    }


def test_empresa_foguete_metadata():
    r = EmpresaFogueteRule()
    assert r.codigo == "EMPRESA_FOGUETE"
    assert r.versao_atual == "1.0.0"
    assert r.severidade_padrao == "forte"
    assert "automatizado" in r.disclaimer
```

Run:

```bash
pytest -v
```

Expected: 2 new tests pass.

- [ ] **Step 8: Commit**

```bash
git add apps/etl/
git commit -m "feat(etl): alerts engine + skeleton rules + EMPRESA_FOGUETE complete"
```

---

## Fase 1.6 — Infra Docker

### Task 30: docker-compose para dev local

**Files:**
- Create: `infra/docker-compose.yml`
- Create: `infra/.env.example`

- [ ] **Step 1: docker-compose.yml**

```yaml
version: "3.9"

services:
  postgres:
    image: postgis/postgis:16-3.4
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: olho_publico
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 10

  etl:
    build:
      context: ../apps/etl
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/olho_publico
      LOG_LEVEL: INFO
    env_file:
      - .env
    volumes:
      - ../apps/etl:/app
    command: ["python", "-m", "olho_publico_etl"]
    profiles: ["etl"]

volumes:
  postgres_data:
```

- [ ] **Step 2: postgres-init/01-extensions.sql**

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- PostGIS já vem na imagem postgis/postgis
```

- [ ] **Step 3: infra/.env.example**

```
TRANSPARENCIA_API_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_RAW=olho-publico-raw
R2_BUCKET_BRONZE=olho-publico-bronze
R2_BUCKET_BACKUPS=olho-publico-backups
```

- [ ] **Step 4: Commit**

```bash
mkdir -p infra/postgres-init
git add infra/
git commit -m "chore(infra): docker-compose with postgis + etl service"
```

---

### Task 31: Caddy + docker-compose de produção

**Files:**
- Create: `infra/docker-compose.prod.yml`
- Create: `infra/caddy/Caddyfile`
- Create: `infra/portainer/stack-instructions.md`

- [ ] **Step 1: caddy/Caddyfile**

```
{
  email contato@olhopublico.org
}

# Postgres exposto via TLS para Vercel — IP allow-list configurada no firewall do provedor
postgres.olhopublico.org:5433 {
  reverse_proxy postgres:5432 {
    transport http {
      versions h2c
    }
  }
}

# Painel Dagster (futuro), proteção via basic auth
dagster.olhopublico.org {
  basic_auth {
    admin {{ DAGSTER_PASSWORD_HASH }}
  }
  reverse_proxy dagster:3000
}
```

- [ ] **Step 2: docker-compose.prod.yml**

```yaml
version: "3.9"

services:
  postgres:
    image: postgis/postgis:16-3.4
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: olho_publico
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s

  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "5433:5433"
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

  etl:
    image: ghcr.io/${GITHUB_REPO}/etl:latest
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/olho_publico
      TRANSPARENCIA_API_KEY: ${TRANSPARENCIA_API_KEY}
      R2_ACCOUNT_ID: ${R2_ACCOUNT_ID}
      R2_ACCESS_KEY_ID: ${R2_ACCESS_KEY_ID}
      R2_SECRET_ACCESS_KEY: ${R2_SECRET_ACCESS_KEY}

  postgres-backup:
    image: postgres:16-alpine
    restart: unless-stopped
    depends_on:
      - postgres
    environment:
      PGUSER: ${POSTGRES_USER}
      PGPASSWORD: ${POSTGRES_PASSWORD}
      PGHOST: postgres
      PGDATABASE: olho_publico
      R2_BUCKET: ${R2_BUCKET_BACKUPS}
    volumes:
      - ./scripts/backup.sh:/backup.sh:ro
    entrypoint: ["/bin/sh", "-c", "while true; do sh /backup.sh; sleep 86400; done"]

volumes:
  postgres_data:
  caddy_data:
  caddy_config:
```

- [ ] **Step 3: scripts/backup.sh**

```bash
#!/bin/sh
set -e

DATE=$(date -u +%Y%m%d-%H%M%S)
DUMP_FILE="/tmp/olho_publico_${DATE}.sql.gz"

pg_dump --no-owner --no-acl | gzip > "${DUMP_FILE}"

# Upload para R2 via aws-cli (instalar em image custom em produção)
aws s3 cp "${DUMP_FILE}" "s3://${R2_BUCKET}/postgres/${DATE}.sql.gz" \
  --endpoint-url "https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

rm "${DUMP_FILE}"
echo "Backup ${DATE} enviado."
```

- [ ] **Step 4: portainer/stack-instructions.md**

```markdown
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
```

- [ ] **Step 5: Commit**

```bash
mkdir -p infra/scripts
git add infra/
git commit -m "chore(infra): Caddy + docker-compose prod + Portainer stack instructions"
```

---

## Fase 1.7 — CI/CD

### Task 32: GitHub Actions

**Files:**
- Create: `.github/workflows/web-ci.yml`
- Create: `.github/workflows/etl-ci.yml`

- [ ] **Step 1: web-ci.yml**

```yaml
name: web-ci

on:
  push:
    branches: [main]
    paths:
      - "apps/web/**"
      - "packages/**"
      - "pnpm-workspace.yaml"
  pull_request:
    paths:
      - "apps/web/**"
      - "packages/**"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter @olho/shared test
      - run: pnpm --filter @olho/db typecheck
      - run: pnpm --filter web typecheck
      - run: pnpm --filter web lint
      - run: pnpm --filter web build
        env:
          NEXT_PUBLIC_SITE_URL: https://olhopublico.org
          DATABASE_URL: postgresql://placeholder@localhost/x
```

- [ ] **Step 2: etl-ci.yml**

```yaml
name: etl-ci

on:
  push:
    branches: [main]
    paths:
      - "apps/etl/**"
  pull_request:
    paths:
      - "apps/etl/**"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -e "apps/etl[dev]"
      - run: ruff check apps/etl
      - run: pytest apps/etl -v --cov=apps/etl/olho_publico_etl

  docker:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: apps/etl
          push: true
          tags: ghcr.io/${{ github.repository }}/etl:latest
```

- [ ] **Step 3: Commit**

```bash
git add .github/
git commit -m "ci: github actions for web (lint+typecheck+build) and etl (test+docker)"
```

---

## Fase 1.8 — Documentação

### Task 33: README e CONTRIBUTING completos

**Files:**
- Modify: `README.md` (substituir placeholder)
- Create: `CONTRIBUTING.md`
- Create: `LICENSE`
- Create: `docs/HANDOFF.md`
- Create: `docs/METODOLOGIA.md`
- Create: `docs/DECISIONS.md`

- [ ] **Step 1: README.md (substituir)**

```markdown
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

# Sobe Postgres local
docker compose -f infra/docker-compose.yml up -d postgres

# Aplica schema
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
```

- [ ] **Step 2: CONTRIBUTING.md**

```markdown
# Como contribuir

Olho Público é um projeto cívico aberto a contribuições de jornalistas, devs, designers e qualquer pessoa preocupada com transparência pública.

## Tipos de contribuição valiosa

- **Scrapers de prefeitura** — investigar portais municipais e implementar (ou melhorar) scrapers para os 4 ERPs principais (E&L, IPM, Betha, Equiplano)
- **Regras de alerta** — propor novas regras de detecção (em `apps/etl/olho_publico_etl/alerts/rules/`) sempre acompanhadas de testes e documentação metodológica
- **UI/UX** — melhorias no front, em particular acessibilidade e mobile
- **Documentação** — explicações em linguagem simples na metodologia

## Processo

1. Abra uma issue descrevendo o que pretende
2. Fork → branch (`feat/nome-curto`) → PR
3. PR precisa passar em CI (`pnpm test`, `pytest`, lint, typecheck)
4. Toda nova regra de alerta exige:
   - Teste unitário com fixtures
   - Atualização em `docs/METODOLOGIA.md`
   - Bump de `versao_atual` se mudar comportamento

## Estilo de código

- TypeScript strict; eslint configurado em `apps/web`
- Python ruff + mypy em `apps/etl`
- Commits em português, padrão `tipo(escopo): mensagem` (`feat(web):`, `fix(etl):`, `docs:`)

## Boas práticas com dados públicos

- Toda nova fonte deve gravar **raw** original no R2 antes de qualquer parsing
- CPFs sempre mascarados (use `mask_cpf` de `utils/cpf_mask.py`)
- Disclaimers obrigatórios em qualquer regra de alerta
```

- [ ] **Step 3: LICENSE**

```
Olho Público — Source-Available License (não-comercial), v1.0
Copyright (c) 2026 Olho Público

Concede-se permissão, gratuita, a qualquer pessoa que obtenha uma cópia
deste software e arquivos de documentação associados (o "Software"), para
ler, estudar, modificar e distribuir o Software para fins NÃO COMERCIAIS,
incluindo:

  - uso jornalístico
  - uso acadêmico e de pesquisa
  - uso cívico e educacional
  - contribuição de melhorias ao próprio projeto

USO COMERCIAL — incluindo venda do Software, hospedagem como serviço
comercial, integração em produto comercial, ou exploração econômica
direta — exige licença comercial separada concedida pelos detentores do
copyright. Entre em contato em contato@olhopublico.org.

O Software é fornecido "COMO ESTÁ", sem garantia de qualquer tipo,
expressa ou implícita, incluindo mas não limitada a garantias de
comercialização, adequação a propósito específico e não-violação. Em
nenhum caso os autores ou detentores de copyright serão responsáveis
por qualquer reclamação, dano ou outra responsabilidade, seja em ação
contratual, delito ou de outra natureza, decorrente de, ou em conexão
com o Software ou o uso ou outras transações no Software.
```

- [ ] **Step 4: docs/METODOLOGIA.md**

```markdown
# Metodologia

> Este documento é a versão canônica e versionada da metodologia mostrada em `/metodologia` no site. Mudanças aqui exigem atualização da regra correspondente em `apps/etl/olho_publico_etl/alerts/rules/` e bump de versão.

## Princípios

1. Fato antes de opinião
2. Sinais não são acusações — todo alerta tem disclaimer e link para evidência
3. Cobertura nacional desde o dia 1
4. Transparência da metodologia (esta seção, versionada)

## Fontes (V1)

| Fonte | Origem | Ingestão |
|---|---|---|
| Portal da Transparência | api.portaldatransparencia.gov.br | API REST diária |
| Receita Federal CNPJ | dados.gov.br/dataset/cnpj | Download mensal + DuckDB |
| CEIS / CNEP | portaldatransparencia.gov.br/sancoes | CSV semanal |
| TSE Doações | dadosabertos.tse.jus.br | Download por eleição |
| Compras.gov.br | compras.dados.gov.br | API REST diária |
| IBGE | ibge.gov.br | CSV/Shapefile anual |
| Portais municipais (ERPs) | E&L, IPM, Betha, Equiplano | Scraper Python por ERP |

## Regras de alerta (V1)

Cada regra é versionada em código (`apps/etl/olho_publico_etl/alerts/rules/`) e levantada com semver (`versao_atual`).

### EMPRESA_FOGUETE — v1.0.0
**Lógica:** CNPJ aberto há <12 meses recebeu contrato >R$ 500.000.
**Severidade padrão:** forte.
**Fontes:** Receita Federal (data de abertura) + Portal da Transparência ou Compras.gov (contrato).

### DISPENSA_SUSPEITA — v1.0.0
**Lógica:** Contrato sem licitação (modalidade DISPENSA) acima de R$ 1.000.000.
**Severidade padrão:** atenção.

### SOCIO_SANCIONADO — v1.0.0
**Lógica:** Empresa cujo sócio aparece em CEIS ou CNEP firma novo contrato público.
**Severidade padrão:** forte.

### CRESCIMENTO_ANOMALO — v1.0.0
**Lógica:** Empresa cujo faturamento público total cresceu mais de 300% (>=4x) em relação ao ano anterior.
**Severidade padrão:** atenção.

### CONCENTRACAO — v1.0.0
**Lógica:** Mesma empresa concentra mais de 40% dos contratos de um órgão/secretaria em um ano.
**Severidade padrão:** informativo.

### DOADOR_BENEFICIADO — v1.0.0
**Lógica:** Empresa que doou para a campanha vitoriosa de prefeito recebe contrato da prefeitura após o início do mandato.
**Severidade padrão:** atenção.

## Disclaimer obrigatório

> "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa."

## Direito de resposta

Toda página tem botão para contestar. Contestações procedentes são publicadas vinculadas ao registro original.
```

- [ ] **Step 5: docs/DECISIONS.md**

```markdown
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
```

- [ ] **Step 6: docs/HANDOFF.md** (a sequência exata para o usuário quando voltar)

```markdown
# Handoff — o que falta para o Olho Público entrar no ar

> Plano P1 (scaffolding) executado autonomamente. Para destravar P2 em diante, complete os passos abaixo na ordem.

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
- [ ] Aplicar migration: `docker exec olho-publico-etl pnpm db:migrate` (ou rodar via container Node temporário)

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
4. Seguir para P3 em diante

## Anexos

- [Spec completa de V1](superpowers/specs/2026-04-22-olho-publico-design.md)
- [Plano P1 (este já executado)](superpowers/plans/2026-04-22-olho-publico-p1-scaffolding.md)
- [Metodologia](METODOLOGIA.md)
- [ADRs](DECISIONS.md)
```

- [ ] **Step 7: Commit**

```bash
git add README.md CONTRIBUTING.md LICENSE docs/
git commit -m "docs: README, CONTRIBUTING, LICENSE, METODOLOGIA, DECISIONS, HANDOFF"
```

---

## Fase 1.9 — Validação final

### Task 34: Smoke test completo

- [ ] **Step 1: Garantir build do site**

```bash
cd /Users/felipeabreu/Documents/Apps/gov
pnpm install
pnpm --filter web build
```

Expected: `pnpm build` finaliza sem erros.

- [ ] **Step 2: Rodar testes**

```bash
pnpm --filter @olho/shared test
cd apps/etl && source .venv/bin/activate && pytest -v
```

Expected: todos os testes passam.

- [ ] **Step 3: Verificar páginas no dev**

```bash
pnpm dev
```

Acessar em sequência e verificar:
- http://localhost:3000 (home)
- http://localhost:3000/cidade/SP/sao-paulo (storytelling)
- http://localhost:3000/cidade/SP/sao-paulo/dashboard
- http://localhost:3000/empresa/12345678000190
- http://localhost:3000/busca?q=sao
- http://localhost:3000/metodologia
- http://localhost:3000/contestar
- http://localhost:3000/privacidade

- [ ] **Step 4: Commit final do milestone P1**

```bash
git add -A
git commit -m "chore: P1 milestone complete — scaffolding ready for P2 (data ingestion)" --allow-empty
git tag p1-complete
```

---

## Self-review check

- [x] Todas as tarefas têm caminhos de arquivos exatos
- [x] Sem placeholders em código que precisa rodar
- [x] Componentes referenciados em tasks posteriores são definidos em tasks anteriores
- [x] Tipos do schema (Drizzle) são consistentes com tipos Pydantic (snake_case no Postgres, mapeado em ambos)
- [x] Tasks são bite-sized (cada step é executável isoladamente)
- [x] Cobre toda a Seção "fundação" do spec (frontend, backend, schema, mocks, docs, infra)
- [x] Deixa explícito o que vai para os próximos planos (P2-P9) com `NotImplementedError` ou comentários `# Implementação plena em plano PN`
