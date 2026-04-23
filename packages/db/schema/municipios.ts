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
    nomeIdx: index("idx_municipios_nome_trgm").using("gin", t.nome.op("gin_trgm_ops")),
  })
);

export type Municipio = typeof municipios.$inferSelect;
export type MunicipioInsert = typeof municipios.$inferInsert;
