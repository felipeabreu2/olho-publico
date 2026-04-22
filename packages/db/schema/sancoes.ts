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
