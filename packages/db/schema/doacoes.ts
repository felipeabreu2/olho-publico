import { pgTable, varchar, text, integer, numeric, serial, index } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";

export const doacoes = pgTable(
  "doacoes",
  {
    id: serial("id").primaryKey(),
    cnpjDoador: varchar("cnpj_doador", { length: 14 }),
    cpfDoadorMascarado: varchar("cpf_doador_mascarado", { length: 14 }),
    candidatoNome: text("candidato_nome").notNull(),
    candidatoCargo: varchar("candidato_cargo", { length: 50 }).notNull(),
    partido: varchar("partido", { length: 20 }),
    valor: numeric("valor", { precision: 18, scale: 2 }).notNull(),
    anoEleicao: integer("ano_eleicao").notNull(),
    municipioId: varchar("municipio_id", { length: 7 }).references(() => municipios.idIbge),
  },
  (t) => ({
    cnpjIdx: index("idx_doacoes_cnpj").on(t.cnpjDoador),
    candidatoIdx: index("idx_doacoes_candidato").on(t.candidatoNome),
    municipioAnoIdx: index("idx_doacoes_municipio_ano").on(t.municipioId, t.anoEleicao),
  })
);

export type Doacao = typeof doacoes.$inferSelect;
export type DoacaoInsert = typeof doacoes.$inferInsert;
