export type UF =
  | "AC" | "AL" | "AP" | "AM" | "BA" | "CE" | "DF" | "ES" | "GO"
  | "MA" | "MT" | "MS" | "MG" | "PA" | "PB" | "PR" | "PE" | "PI"
  | "RJ" | "RN" | "RS" | "RO" | "RR" | "SC" | "SP" | "SE" | "TO";

export type SeveridadeAlerta = "info" | "atencao" | "forte";

export interface AlertaDisplay {
  id: number;
  tipo: string;
  tituloLegivel: string;
  resumoLegivel: string;
  severidade: SeveridadeAlerta;
  dataDeteccao: string;
  evidencia: Record<string, unknown>;
  disclaimer: string;
  metodologiaUrl: string;
}
