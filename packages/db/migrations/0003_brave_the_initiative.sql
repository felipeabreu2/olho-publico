CREATE TABLE IF NOT EXISTS "programas_sociais" (
	"id" serial PRIMARY KEY NOT NULL,
	"municipio_id" varchar(7) NOT NULL,
	"programa" varchar(50) NOT NULL,
	"ano_mes" varchar(7) NOT NULL,
	"qtd_beneficiarios" integer,
	"valor_total" numeric(18, 2) NOT NULL,
	"valor_medio_beneficiario" numeric(18, 2),
	"fonte" text DEFAULT 'portal_transparencia' NOT NULL,
	CONSTRAINT "uq_programas_sociais" UNIQUE("municipio_id","programa","ano_mes")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "pessoas_pep" (
	"id" serial PRIMARY KEY NOT NULL,
	"cpf_mascarado" varchar(14) NOT NULL,
	"nome" text NOT NULL,
	"cargo" text,
	"orgao" text,
	"data_inicio" date,
	"data_fim" date,
	"fonte" text DEFAULT 'portal_transparencia' NOT NULL,
	"atualizado_em" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "programas_sociais" ADD CONSTRAINT "programas_sociais_municipio_id_municipios_id_ibge_fk" FOREIGN KEY ("municipio_id") REFERENCES "public"."municipios"("id_ibge") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_programas_sociais_municipio" ON "programas_sociais" USING btree ("municipio_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_programas_sociais_programa_ano" ON "programas_sociais" USING btree ("programa","ano_mes");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_pep_cpf" ON "pessoas_pep" USING btree ("cpf_mascarado");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_pep_nome_trgm" ON "pessoas_pep" USING gin ("nome" gin_trgm_ops);