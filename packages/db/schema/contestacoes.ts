import { pgTable, varchar, text, timestamp, serial, pgEnum } from "drizzle-orm/pg-core";

export const tipoAlvoEnum = pgEnum("tipo_alvo_contestacao", ["alerta", "contrato", "empresa", "municipio"]);
export const statusContestacaoEnum = pgEnum("status_contestacao", [
  "pendente",
  "em_analise",
  "respondida",
  "arquivada",
]);

export const contestacoes = pgTable("contestacoes", {
  id: serial("id").primaryKey(),
  tipoAlvo: tipoAlvoEnum("tipo_alvo").notNull(),
  idAlvo: text("id_alvo").notNull(),
  emailSolicitante: text("email_solicitante").notNull(),
  mensagem: text("mensagem").notNull(),
  status: statusContestacaoEnum("status").notNull().default("pendente"),
  resposta: text("resposta"),
  dataSolicitacao: timestamp("data_solicitacao", { withTimezone: true }).defaultNow().notNull(),
  dataResposta: timestamp("data_resposta", { withTimezone: true }),
});

export type Contestacao = typeof contestacoes.$inferSelect;
export type ContestacaoInsert = typeof contestacoes.$inferInsert;
