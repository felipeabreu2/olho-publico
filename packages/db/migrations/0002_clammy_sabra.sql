ALTER TABLE "municipios" DROP CONSTRAINT "municipios_slug_unique";--> statement-breakpoint
ALTER TABLE "municipios" ADD CONSTRAINT "uq_municipios_uf_slug" UNIQUE("uf","slug");