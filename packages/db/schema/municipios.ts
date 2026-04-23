import { pgTable, varchar, integer, text, real, timestamp, pgEnum, index, unique } from "drizzle-orm/pg-core";

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
    // Não global-unique: Brasil tem cidades de mesmo nome em estados diferentes
    // (ex: "Bom Jesus do Tocantins" em PA e TO). Unicidade real é (uf, slug).
    slug: varchar("slug", { length: 120 }).notNull(),
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
    nomeIdx: index("idx_municipios_nome_trgm").using("gin", t.nome.op("gin_trgm_ops")),
    ufSlugUnique: unique("uq_municipios_uf_slug").on(t.uf, t.slug),
  })
);

export type Municipio = typeof municipios.$inferSelect;
export type MunicipioInsert = typeof municipios.$inferInsert;
