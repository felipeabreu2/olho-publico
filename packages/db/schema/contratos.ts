import { pgTable, varchar, text, date, numeric, serial, pgEnum, index } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";
import { empresas } from "./empresas";

export const fonteContratoEnum = pgEnum("fonte_contrato", [
  "portal_transparencia",
  "compras_gov",
  "prefeitura_el",
  "prefeitura_ipm",
  "prefeitura_betha",
  "prefeitura_equiplano",
]);

export const contratos = pgTable(
  "contratos",
  {
    id: serial("id").primaryKey(),
    municipioAplicacaoId: varchar("municipio_aplicacao_id", { length: 7 }).references(() => municipios.idIbge),
    cnpjFornecedor: varchar("cnpj_fornecedor", { length: 14 }).references(() => empresas.cnpj),
    orgaoContratante: text("orgao_contratante").notNull(),
    objeto: text("objeto").notNull(),
    valor: numeric("valor", { precision: 18, scale: 2 }).notNull(),
    dataAssinatura: date("data_assinatura").notNull(),
    modalidadeLicitacao: varchar("modalidade_licitacao", { length: 50 }),
    fonte: fonteContratoEnum("fonte").notNull(),
    dadosOriginaisUrl: text("dados_originais_url"),
  },
  (t) => ({
    municipioDataIdx: index("idx_contratos_municipio_data").on(t.municipioAplicacaoId, t.dataAssinatura),
    fornecedorIdx: index("idx_contratos_fornecedor").on(t.cnpjFornecedor),
    objetoFtsIdx: index("idx_contratos_objeto_fts").using("gin", t.objeto.op("gin_trgm_ops")),
  })
);

export type Contrato = typeof contratos.$inferSelect;
export type ContratoInsert = typeof contratos.$inferInsert;
