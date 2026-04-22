CREATE TYPE "public"."cobertura_prefeitura" AS ENUM('nenhuma', 'parcial', 'completa');--> statement-breakpoint
CREATE TYPE "public"."fonte_contrato" AS ENUM('portal_transparencia', 'compras_gov', 'prefeitura_el', 'prefeitura_ipm', 'prefeitura_betha', 'prefeitura_equiplano');--> statement-breakpoint
CREATE TYPE "public"."severidade_alerta" AS ENUM('info', 'atencao', 'forte');--> statement-breakpoint
CREATE TYPE "public"."status_contestacao" AS ENUM('pendente', 'em_analise', 'respondida', 'arquivada');--> statement-breakpoint
CREATE TYPE "public"."tipo_alvo_contestacao" AS ENUM('alerta', 'contrato', 'empresa', 'municipio');--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "municipios" (
	"id_ibge" varchar(7) PRIMARY KEY NOT NULL,
	"nome" text NOT NULL,
	"slug" varchar(120) NOT NULL,
	"uf" varchar(2) NOT NULL,
	"populacao" integer,
	"idh" real,
	"geometria" text,
	"prefeito_nome" text,
	"prefeito_partido" varchar(20),
	"cobertura_prefeitura" "cobertura_prefeitura" DEFAULT 'nenhuma' NOT NULL,
	"erp_detectado" varchar(30),
	"atualizado_em" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "municipios_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "empresas" (
	"cnpj" varchar(14) PRIMARY KEY NOT NULL,
	"razao_social" text NOT NULL,
	"nome_fantasia" text,
	"data_abertura" date,
	"situacao" varchar(30),
	"cnae_principal" varchar(7),
	"municipio_sede_id" varchar(7),
	"flags" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"atualizado_em" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "socios" (
	"id" serial PRIMARY KEY NOT NULL,
	"cnpj" varchar(14) NOT NULL,
	"cpf_mascarado" varchar(14),
	"nome" text NOT NULL,
	"tipo" varchar(30),
	"data_entrada" date
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "contratos" (
	"id" serial PRIMARY KEY NOT NULL,
	"municipio_aplicacao_id" varchar(7),
	"cnpj_fornecedor" varchar(14),
	"orgao_contratante" text NOT NULL,
	"objeto" text NOT NULL,
	"valor" numeric(18, 2) NOT NULL,
	"data_assinatura" date NOT NULL,
	"modalidade_licitacao" varchar(50),
	"fonte" "fonte_contrato" NOT NULL,
	"dados_originais_url" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "sancoes" (
	"id" serial PRIMARY KEY NOT NULL,
	"cnpj" varchar(14) NOT NULL,
	"tipo_sancao" varchar(50) NOT NULL,
	"orgao_sancionador" text NOT NULL,
	"data_inicio" date NOT NULL,
	"data_fim" date,
	"motivo" text,
	"fonte_url" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "doacoes" (
	"id" serial PRIMARY KEY NOT NULL,
	"cnpj_doador" varchar(14),
	"cpf_doador_mascarado" varchar(14),
	"candidato_nome" text NOT NULL,
	"candidato_cargo" varchar(50) NOT NULL,
	"partido" varchar(20),
	"valor" numeric(18, 2) NOT NULL,
	"ano_eleicao" integer NOT NULL,
	"municipio_id" varchar(7)
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "agregacoes_municipio" (
	"municipio_id" varchar(7) NOT NULL,
	"ano_referencia" integer NOT NULL,
	"total_contratos_federais" numeric(18, 2) DEFAULT '0' NOT NULL,
	"total_contratos_prefeitura" numeric(18, 2) DEFAULT '0' NOT NULL,
	"qtd_contratos_federais" integer DEFAULT 0 NOT NULL,
	"qtd_contratos_prefeitura" integer DEFAULT 0 NOT NULL,
	"top_fornecedores" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"gastos_por_area" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"comparacao_similares" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"atualizado_em" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "agregacoes_municipio_municipio_id_ano_referencia_pk" PRIMARY KEY("municipio_id","ano_referencia")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "regras_alerta" (
	"codigo" varchar(50) PRIMARY KEY NOT NULL,
	"nome" text NOT NULL,
	"descricao" text NOT NULL,
	"versao_atual" varchar(20) NOT NULL,
	"parametros" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"disclaimer_text" text NOT NULL,
	"criada_em" timestamp with time zone DEFAULT now() NOT NULL,
	"atualizada_em" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "alertas" (
	"id" serial PRIMARY KEY NOT NULL,
	"tipo" varchar(50) NOT NULL,
	"severidade" "severidade_alerta" NOT NULL,
	"municipio_id" varchar(7),
	"cnpj_envolvido" varchar(14),
	"evidencia" jsonb NOT NULL,
	"data_deteccao" timestamp with time zone DEFAULT now() NOT NULL,
	"regra_versao" varchar(20) NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "contestacoes" (
	"id" serial PRIMARY KEY NOT NULL,
	"tipo_alvo" "tipo_alvo_contestacao" NOT NULL,
	"id_alvo" text NOT NULL,
	"email_solicitante" text NOT NULL,
	"mensagem" text NOT NULL,
	"status" "status_contestacao" DEFAULT 'pendente' NOT NULL,
	"resposta" text,
	"data_solicitacao" timestamp with time zone DEFAULT now() NOT NULL,
	"data_resposta" timestamp with time zone
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "empresas" ADD CONSTRAINT "empresas_municipio_sede_id_municipios_id_ibge_fk" FOREIGN KEY ("municipio_sede_id") REFERENCES "public"."municipios"("id_ibge") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "socios" ADD CONSTRAINT "socios_cnpj_empresas_cnpj_fk" FOREIGN KEY ("cnpj") REFERENCES "public"."empresas"("cnpj") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "contratos" ADD CONSTRAINT "contratos_municipio_aplicacao_id_municipios_id_ibge_fk" FOREIGN KEY ("municipio_aplicacao_id") REFERENCES "public"."municipios"("id_ibge") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "contratos" ADD CONSTRAINT "contratos_cnpj_fornecedor_empresas_cnpj_fk" FOREIGN KEY ("cnpj_fornecedor") REFERENCES "public"."empresas"("cnpj") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "sancoes" ADD CONSTRAINT "sancoes_cnpj_empresas_cnpj_fk" FOREIGN KEY ("cnpj") REFERENCES "public"."empresas"("cnpj") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "doacoes" ADD CONSTRAINT "doacoes_municipio_id_municipios_id_ibge_fk" FOREIGN KEY ("municipio_id") REFERENCES "public"."municipios"("id_ibge") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "agregacoes_municipio" ADD CONSTRAINT "agregacoes_municipio_municipio_id_municipios_id_ibge_fk" FOREIGN KEY ("municipio_id") REFERENCES "public"."municipios"("id_ibge") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "alertas" ADD CONSTRAINT "alertas_tipo_regras_alerta_codigo_fk" FOREIGN KEY ("tipo") REFERENCES "public"."regras_alerta"("codigo") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "alertas" ADD CONSTRAINT "alertas_municipio_id_municipios_id_ibge_fk" FOREIGN KEY ("municipio_id") REFERENCES "public"."municipios"("id_ibge") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "alertas" ADD CONSTRAINT "alertas_cnpj_envolvido_empresas_cnpj_fk" FOREIGN KEY ("cnpj_envolvido") REFERENCES "public"."empresas"("cnpj") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_municipios_uf" ON "municipios" USING btree ("uf");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_municipios_nome_trgm" ON "municipios" USING gin ("nome");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_empresas_razao_social_trgm" ON "empresas" USING gin ("razao_social");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_empresas_flags" ON "empresas" USING gin ("flags");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_empresas_sede" ON "empresas" USING btree ("municipio_sede_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_socios_cnpj" ON "socios" USING btree ("cnpj");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_socios_nome_trgm" ON "socios" USING gin ("nome");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_contratos_municipio_data" ON "contratos" USING btree ("municipio_aplicacao_id","data_assinatura");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_contratos_fornecedor" ON "contratos" USING btree ("cnpj_fornecedor");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_contratos_objeto_fts" ON "contratos" USING gin ("objeto");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_sancoes_cnpj" ON "sancoes" USING btree ("cnpj");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_doacoes_cnpj" ON "doacoes" USING btree ("cnpj_doador");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_doacoes_candidato" ON "doacoes" USING btree ("candidato_nome");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_doacoes_municipio_ano" ON "doacoes" USING btree ("municipio_id","ano_eleicao");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_alertas_municipio_data" ON "alertas" USING btree ("municipio_id","data_deteccao");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_alertas_cnpj" ON "alertas" USING btree ("cnpj_envolvido");