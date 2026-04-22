import { pgTable, varchar, integer, numeric, jsonb, timestamp, primaryKey } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";

export interface TopFornecedor {
  cnpj: string;
  razaoSocial: string;
  totalContratos: number;
  valorTotal: string;
}

export interface GastosPorArea {
  area: string;
  valor: string;
  percentual: number;
}

export interface ComparacaoSimilar {
  municipioId: string;
  municipioNome: string;
  uf: string;
  metric: string;
  valorComparado: string;
}

export const agregacoesMunicipio = pgTable(
  "agregacoes_municipio",
  {
    municipioId: varchar("municipio_id", { length: 7 }).notNull().references(() => municipios.idIbge),
    anoReferencia: integer("ano_referencia").notNull(),
    totalContratosFederais: numeric("total_contratos_federais", { precision: 18, scale: 2 }).default("0").notNull(),
    totalContratosPrefeitura: numeric("total_contratos_prefeitura", { precision: 18, scale: 2 }).default("0").notNull(),
    qtdContratosFederais: integer("qtd_contratos_federais").default(0).notNull(),
    qtdContratosPrefeitura: integer("qtd_contratos_prefeitura").default(0).notNull(),
    topFornecedores: jsonb("top_fornecedores").$type<TopFornecedor[]>().default([]).notNull(),
    gastosPorArea: jsonb("gastos_por_area").$type<GastosPorArea[]>().default([]).notNull(),
    comparacaoSimilares: jsonb("comparacao_similares").$type<ComparacaoSimilar[]>().default([]).notNull(),
    atualizadoEm: timestamp("atualizado_em", { withTimezone: true }).defaultNow().notNull(),
  },
  (t) => ({
    pk: primaryKey({ columns: [t.municipioId, t.anoReferencia] }),
  })
);

export type AgregacaoMunicipio = typeof agregacoesMunicipio.$inferSelect;
export type AgregacaoMunicipioInsert = typeof agregacoesMunicipio.$inferInsert;
