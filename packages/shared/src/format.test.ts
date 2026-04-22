import { describe, it, expect } from "vitest";
import { formatBRL, formatCNPJ, slugify } from "./index";

describe("formatBRL", () => {
  it("formats large values", () => {
    expect(formatBRL(1234567.89)).toMatch(/R\$\s?1\.234\.567,89/);
  });
  it("returns em-dash for NaN", () => {
    expect(formatBRL("abc")).toBe("—");
  });
});

describe("formatCNPJ", () => {
  it("masks bare digits", () => {
    expect(formatCNPJ("12345678000190")).toBe("12.345.678/0001-90");
  });
});

describe("slugify", () => {
  it("removes accents and lowercases", () => {
    expect(slugify("São Paulo")).toBe("sao-paulo");
  });
  it("handles dashes and uppercase UF", () => {
    expect(slugify("Itabaiana - SE")).toBe("itabaiana-se");
  });
});
