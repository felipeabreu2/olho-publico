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
    nomeIdx: index("idx_socios_nome_trgm").using("gin", t.nome.op("gin_trgm_ops")),
  })
);

export type Socio = typeof socios.$inferSelect;
export type SocioInsert = typeof socios.$inferInsert;
