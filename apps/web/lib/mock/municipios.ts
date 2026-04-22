import type { Municipio } from "@olho/db";
import type { AgregacaoMunicipio } from "@olho/db";

export const mockMunicipios: Municipio[] = [
  {
    idIbge: "3550308",
    nome: "São Paulo",
    slug: "sao-paulo",
    uf: "SP",
    populacao: 12325232,
    idh: 0.805,
    geometria: null,
    prefeitoNome: "Ricardo Nunes",
    prefeitoPartido: "MDB",
    coberturaPrefeitura: "parcial",
    erpDetectado: "el",
    atualizadoEm: new Date(),
  },
  {
    idIbge: "2611606",
    nome: "Recife",
    slug: "recife",
    uf: "PE",
    populacao: 1488920,
    idh: 0.772,
    geometria: null,
    prefeitoNome: "João Campos",
    prefeitoPartido: "PSB",
    coberturaPrefeitura: "parcial",
    erpDetectado: "betha",
    atualizadoEm: new Date(),
  },
  {
    idIbge: "2802502",
    nome: "Itabaiana",
    slug: "itabaiana",
    uf: "SE",
    populacao: 96776,
    idh: 0.642,
    geometria: null,
    prefeitoNome: "Adailton de Souza",
    prefeitoPartido: "PP",
    coberturaPrefeitura: "nenhuma",
    erpDetectado: null,
    atualizadoEm: new Date(),
  },
];

export const mockAgregacoes: Record<string, AgregacaoMunicipio> = {
  "3550308": {
    municipioId: "3550308",
    anoReferencia: 2025,
    totalContratosFederais: "8420000000",
    totalContratosPrefeitura: "12300000000",
    qtdContratosFederais: 4821,
    qtdContratosPrefeitura: 8026,
    topFornecedores: [
      { cnpj: "12345678000190", razaoSocial: "Construtora Alpha S.A.", totalContratos: 38, valorTotal: "342000000" },
      { cnpj: "23456789000101", razaoSocial: "Limpeza Total Serviços Ltda", totalContratos: 12, valorTotal: "184000000" },
      { cnpj: "34567890000112", razaoSocial: "Tech Solutions Brasil", totalContratos: 27, valorTotal: "98000000" },
    ],
    gastosPorArea: [
      { area: "Saúde", valor: "4200000000", percentual: 38 },
      { area: "Educação", valor: "3100000000", percentual: 28 },
      { area: "Obras e Infraestrutura", valor: "2400000000", percentual: 22 },
      { area: "Administração", valor: "880000000", percentual: 8 },
      { area: "Outros", valor: "440000000", percentual: 4 },
    ],
    comparacaoSimilares: [
      { municipioId: "3304557", municipioNome: "Rio de Janeiro", uf: "RJ", metric: "gasto_per_capita", valorComparado: "0.94" },
      { municipioId: "3106200", municipioNome: "Belo Horizonte", uf: "MG", metric: "gasto_per_capita", valorComparado: "1.12" },
    ],
    atualizadoEm: new Date(),
  },
};
