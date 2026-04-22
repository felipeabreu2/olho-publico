const BRL = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 2,
});

const COMPACT_BRL = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  notation: "compact",
  maximumFractionDigits: 1,
});

export function formatBRL(value: number | string): string {
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(n)) return "—";
  return BRL.format(n);
}

export function formatBRLCompact(value: number | string): string {
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(n)) return "—";
  return COMPACT_BRL.format(n);
}

export function formatCNPJ(cnpj: string): string {
  const digits = cnpj.replace(/\D/g, "").padStart(14, "0");
  return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
}

export function formatDate(input: string | Date): string {
  const d = typeof input === "string" ? new Date(input) : input;
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(d);
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("pt-BR").format(n);
}
