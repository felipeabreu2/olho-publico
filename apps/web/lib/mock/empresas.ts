import type { Empresa } from "@olho/db";

export const mockEmpresas: Empresa[] = [
  {
    cnpj: "12345678000190",
    razaoSocial: "Construtora Alpha S.A.",
    nomeFantasia: "Alpha Construções",
    dataAbertura: "1998-03-15",
    situacao: "ATIVA",
    cnaePrincipal: "4120400",
    municipioSedeId: "3550308",
    flags: { sancionada: false, doadora: true },
    atualizadoEm: new Date(),
  },
  {
    cnpj: "99887766000155",
    razaoSocial: "Servicos Express Ltda",
    nomeFantasia: null,
    dataAbertura: "2025-01-08",
    situacao: "ATIVA",
    cnaePrincipal: "8230001",
    municipioSedeId: "3550308",
    flags: { sancionada: false, doadora: false, foguete: true },
    atualizadoEm: new Date(),
  },
];
