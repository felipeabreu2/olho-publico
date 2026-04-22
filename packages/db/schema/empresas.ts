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
