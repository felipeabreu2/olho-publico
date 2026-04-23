import { pgTable, varchar, integer, numeric, text, serial, index, unique } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";

/**
 * Programas sociais federais por município/mês.
 * Cobre Bolsa Família, Auxílio Brasil/Novo BF, Seguro Defeso etc.
 *
 * Granularidade: 1 linha por (municipio, programa, mês de referência).
 * Não rastreia beneficiários individuais (preserva LGPD).
 */
export const programaSocialEnum = ["bolsa_familia", "auxilio_brasil", "seguro_defeso"] as const;

export const programasSociais = pgTable(
  "programas_sociais",
  {
    id: serial("id").primaryKey(),
    municipioId: varchar("municipio_id", { length: 7 })
      .notNull()
      .references(() => municipios.idIbge),
    programa: varchar("programa", { length: 50 }).notNull(),
    anoMes: varchar("ano_mes", { length: 7 }).notNull(), // 'YYYY-MM'
    qtdBeneficiarios: integer("qtd_beneficiarios"),
    valorTotal: numeric("valor_total", { precision: 18, scale: 2 }).notNull(),
    valorMedioBeneficiario: numeric("valor_medio_beneficiario", { precision: 18, scale: 2 }),
    fonte: text("fonte").default("portal_transparencia").notNull(),
  },
  (t) => ({
    uniq: unique("uq_programas_sociais").on(t.municipioId, t.programa, t.anoMes),
    municipioIdx: index("idx_programas_sociais_municipio").on(t.municipioId),
    programaAnoIdx: index("idx_programas_sociais_programa_ano").on(t.programa, t.anoMes),
  })
);

export type ProgramaSocial = typeof programasSociais.$inferSelect;
export type ProgramaSocialInsert = typeof programasSociais.$inferInsert;
