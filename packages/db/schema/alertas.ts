import { pgTable, varchar, jsonb, timestamp, serial, pgEnum, index } from "drizzle-orm/pg-core";
import { municipios } from "./municipios";
import { empresas } from "./empresas";
import { regrasAlerta } from "./regras_alerta";

export const severidadeEnum = pgEnum("severidade_alerta", ["info", "atencao", "forte"]);

export const alertas = pgTable(
  "alertas",
  {
    id: serial("id").primaryKey(),
    tipo: varchar("tipo", { length: 50 }).notNull().references(() => regrasAlerta.codigo),
    severidade: severidadeEnum("severidade").notNull(),
    municipioId: varchar("municipio_id", { length: 7 }).references(() => municipios.idIbge),
    cnpjEnvolvido: varchar("cnpj_envolvido", { length: 14 }).references(() => empresas.cnpj),
    evidencia: jsonb("evidencia").$type<Record<string, unknown>>().notNull(),
    dataDeteccao: timestamp("data_deteccao", { withTimezone: true }).defaultNow().notNull(),
    regraVersao: varchar("regra_versao", { length: 20 }).notNull(),
  },
  (t) => ({
    municipioDataIdx: index("idx_alertas_municipio_data").on(t.municipioId, t.dataDeteccao),
    cnpjIdx: index("idx_alertas_cnpj").on(t.cnpjEnvolvido),
  })
);

export type Alerta = typeof alertas.$inferSelect;
export type AlertaInsert = typeof alertas.$inferInsert;
