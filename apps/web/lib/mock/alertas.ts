import type { AlertaDisplay } from "@olho/shared";

export const mockAlertasSP: AlertaDisplay[] = [
  {
    id: 1,
    tipo: "EMPRESA_FOGUETE",
    tituloLegivel: "Empresa criada há 4 meses recebeu contrato de R$ 12 milhões",
    resumoLegivel:
      "Servicos Express Ltda (CNPJ 99.887.766/0001-55), aberta em janeiro/2025, foi contratada pela Secretaria de Obras de São Paulo em 08/04/2026, sem licitação.",
    severidade: "forte",
    dataDeteccao: "2026-04-22T10:00:00Z",
    evidencia: {
      cnpj: "99887766000155",
      data_abertura: "2025-01-08",
      contrato_id: 102341,
      valor: 12000000,
      modalidade: "DISPENSA",
    },
    disclaimer:
      "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa.",
    metodologiaUrl: "/metodologia#empresa-foguete",
  },
  {
    id: 2,
    tipo: "CONCENTRACAO",
    tituloLegivel: "Construtora Alpha responde por 47% dos contratos da Secretaria de Obras",
    resumoLegivel:
      "Em 2025, a empresa concentra quase metade dos contratos da pasta. Padrão pode indicar dependência ou favorecimento — exige análise detalhada.",
    severidade: "atencao",
    dataDeteccao: "2026-04-15T08:30:00Z",
    evidencia: { cnpj: "12345678000190", percentual: 47, secretaria: "Obras" },
    disclaimer:
      "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa.",
    metodologiaUrl: "/metodologia#concentracao",
  },
  {
    id: 3,
    tipo: "DOADOR_BENEFICIADO",
    tituloLegivel: "Construtora Alpha doou R$ 480 mil para campanha do prefeito atual em 2024",
    resumoLegivel:
      "A mesma empresa que doou para a campanha do prefeito recebeu 38 contratos da prefeitura em 2025, totalizando R$ 342 milhões.",
    severidade: "atencao",
    dataDeteccao: "2026-04-10T14:00:00Z",
    evidencia: {
      cnpj: "12345678000190",
      doacao: 480000,
      ano_eleicao: 2024,
      contratos_pos: 38,
    },
    disclaimer:
      "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa.",
    metodologiaUrl: "/metodologia#doador-beneficiado",
  },
];
