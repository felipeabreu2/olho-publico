import { and, eq } from "drizzle-orm";
import { agregacoesMunicipio } from "@olho/db";
import { db } from "../db";

export async function getAgregacaoAno(municipioId: string, ano: number) {
  const rows = await db
    .select()
    .from(agregacoesMunicipio)
    .where(
      and(
        eq(agregacoesMunicipio.municipioId, municipioId),
        eq(agregacoesMunicipio.anoReferencia, ano)
      )
    )
    .limit(1);
  return rows[0] ?? null;
}
