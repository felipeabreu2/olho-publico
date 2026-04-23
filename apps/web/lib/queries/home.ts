import { sql } from "drizzle-orm";
import { db } from "../db";

export interface HomeStats {
  totalMunicipios: number;
  totalContratos: number;
  totalEmpresas: number;
  valorTotalContratos: string;
  totalSancoes: number;
}

export async function getHomeStats(): Promise<HomeStats> {
  const rows = await db.execute<{
    total_municipios: number;
    total_contratos: number;
    total_empresas: number;
    valor_total: string;
    total_sancoes: number;
  }>(sql`
    SELECT
      (SELECT COUNT(*) FROM municipios)::int AS total_municipios,
      (SELECT COUNT(*) FROM contratos)::int AS total_contratos,
      (SELECT COUNT(*) FROM empresas)::int AS total_empresas,
      (SELECT COALESCE(SUM(valor), 0) FROM contratos)::text AS valor_total,
      (SELECT COUNT(*) FROM sancoes)::int AS total_sancoes
  `);

  // postgres-js retorna array com extras (count, command). Pega o primeiro objeto.
  const r = (rows as unknown as Array<Record<string, unknown>>)[0] ?? {};
  return {
    totalMunicipios: Number(r.total_municipios ?? 0),
    totalContratos: Number(r.total_contratos ?? 0),
    totalEmpresas: Number(r.total_empresas ?? 0),
    valorTotalContratos: String(r.valor_total ?? "0"),
    totalSancoes: Number(r.total_sancoes ?? 0),
  };
}

export interface CidadeDestaque {
  idIbge: string;
  nome: string;
  uf: string;
  slug: string;
  populacao: number | null;
  totalContratosFederais: string;
  qtdContratosFederais: number;
}

export async function getTopCidades(limit = 6): Promise<CidadeDestaque[]> {
  const rows = await db.execute<{
    id_ibge: string;
    nome: string;
    uf: string;
    slug: string;
    populacao: number | null;
    total_contratos_federais: string;
    qtd_contratos_federais: number;
  }>(sql`
    SELECT
      m.id_ibge, m.nome, m.uf, m.slug, m.populacao,
      a.total_contratos_federais::text,
      a.qtd_contratos_federais
    FROM agregacoes_municipio a
    JOIN municipios m ON m.id_ibge = a.municipio_id
    WHERE a.total_contratos_federais > 0
    ORDER BY a.total_contratos_federais DESC
    LIMIT ${limit}
  `);

  const list = rows as unknown as Array<{
    id_ibge: string;
    nome: string;
    uf: string;
    slug: string;
    populacao: number | null;
    total_contratos_federais: string;
    qtd_contratos_federais: number;
  }>;

  return list.map((r) => ({
    idIbge: r.id_ibge,
    nome: r.nome,
    uf: r.uf,
    slug: r.slug,
    populacao: r.populacao,
    totalContratosFederais: r.total_contratos_federais,
    qtdContratosFederais: Number(r.qtd_contratos_federais),
  }));
}

export interface SancaoRecente {
  cnpj: string;
  razaoSocial: string | null;
  tipoSancao: string;
  orgaoSancionador: string;
  dataInicio: string;
}

export async function getSancoesRecentes(limit = 6): Promise<SancaoRecente[]> {
  const rows = await db.execute<{
    cnpj: string;
    razao_social: string | null;
    tipo_sancao: string;
    orgao_sancionador: string;
    data_inicio: string;
  }>(sql`
    SELECT
      s.cnpj,
      e.razao_social,
      s.tipo_sancao,
      s.orgao_sancionador,
      s.data_inicio::text
    FROM sancoes s
    LEFT JOIN empresas e ON e.cnpj = s.cnpj
    ORDER BY s.data_inicio DESC NULLS LAST
    LIMIT ${limit}
  `);

  const list = rows as unknown as Array<{
    cnpj: string;
    razao_social: string | null;
    tipo_sancao: string;
    orgao_sancionador: string;
    data_inicio: string;
  }>;

  return list.map((r) => ({
    cnpj: r.cnpj,
    razaoSocial: r.razao_social,
    tipoSancao: r.tipo_sancao,
    orgaoSancionador: r.orgao_sancionador,
    dataInicio: r.data_inicio,
  }));
}
