import { eq, and, desc } from "drizzle-orm";
import { db } from "../db";
import { municipios, agregacoesMunicipio, alertas } from "@olho/db";

export async function getMunicipioBySlug(uf: string, slug: string) {
  const rows = await db
    .select()
    .from(municipios)
    .where(and(eq(municipios.uf, uf.toUpperCase()), eq(municipios.slug, slug)))
    .limit(1);
  return rows[0] ?? null;
}

export async function getAgregacoesMunicipio(municipioId: string, ano: number) {
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

export async function getAlertasRecentesMunicipio(municipioId: string, limit = 10) {
  return db
    .select()
    .from(alertas)
    .where(eq(alertas.municipioId, municipioId))
    .orderBy(desc(alertas.dataDeteccao))
    .limit(limit);
}
