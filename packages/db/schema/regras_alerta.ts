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
