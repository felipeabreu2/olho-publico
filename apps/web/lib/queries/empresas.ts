import { eq, desc } from "drizzle-orm";
import { db } from "../db";
import { empresas, contratos, sancoes, doacoes } from "@olho/db";

export async function getEmpresaByCnpj(cnpj: string) {
  const rows = await db.select().from(empresas).where(eq(empresas.cnpj, cnpj)).limit(1);
  return rows[0] ?? null;
}

export async function getContratosEmpresa(cnpj: string, limit = 50) {
  return db
    .select()
    .from(contratos)
    .where(eq(contratos.cnpjFornecedor, cnpj))
    .orderBy(desc(contratos.dataAssinatura))
    .limit(limit);
}

export async function getSancoesEmpresa(cnpj: string) {
  return db.select().from(sancoes).where(eq(sancoes.cnpj, cnpj));
}

export async function getDoacoesEmpresa(cnpj: string) {
  return db.select().from(doacoes).where(eq(doacoes.cnpjDoador, cnpj));
}
