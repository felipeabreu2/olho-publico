import { pgTable, varchar, text, date, timestamp, serial, index } from "drizzle-orm/pg-core";

/**
 * Pessoas Politicamente Expostas (PEP) — agregadas no Portal da Transparência.
 *
 * CPF sempre mascarado (LGPD). Útil para cruzamento futuro com sócios de
 * empresas (detecção "sócio PEP").
 */
export const pessoasPep = pgTable(
  "pessoas_pep",
  {
    id: serial("id").primaryKey(),
    cpfMascarado: varchar("cpf_mascarado", { length: 14 }).notNull(),
    nome: text("nome").notNull(),
    cargo: text("cargo"),
    orgao: text("orgao"),
    dataInicio: date("data_inicio"),
    dataFim: date("data_fim"),
    fonte: text("fonte").default("portal_transparencia").notNull(),
    atualizadoEm: timestamp("atualizado_em", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => ({
    cpfIdx: index("idx_pep_cpf").on(t.cpfMascarado),
    nomeIdx: index("idx_pep_nome_trgm").using("gin", t.nome.op("gin_trgm_ops")),
  })
);

export type PessoaPep = typeof pessoasPep.$inferSelect;
export type PessoaPepInsert = typeof pessoasPep.$inferInsert;
