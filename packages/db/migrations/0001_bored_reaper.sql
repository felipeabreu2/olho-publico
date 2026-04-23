DROP INDEX IF EXISTS "idx_municipios_nome_trgm";--> statement-breakpoint
DROP INDEX IF EXISTS "idx_empresas_razao_social_trgm";--> statement-breakpoint
DROP INDEX IF EXISTS "idx_socios_nome_trgm";--> statement-breakpoint
DROP INDEX IF EXISTS "idx_contratos_objeto_fts";--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_municipios_nome_trgm" ON "municipios" USING gin ("nome" gin_trgm_ops);--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_empresas_razao_social_trgm" ON "empresas" USING gin ("razao_social" gin_trgm_ops);--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_socios_nome_trgm" ON "socios" USING gin ("nome" gin_trgm_ops);--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "idx_contratos_objeto_fts" ON "contratos" USING gin ("objeto" gin_trgm_ops);