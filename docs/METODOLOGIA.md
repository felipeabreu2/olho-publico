# Metodologia

> Este documento é a versão canônica e versionada da metodologia mostrada em `/metodologia` no site. Mudanças aqui exigem atualização da regra correspondente em `apps/etl/olho_publico_etl/alerts/rules/` e bump de versão.

## Princípios

1. Fato antes de opinião
2. Sinais não são acusações — todo alerta tem disclaimer e link para evidência
3. Cobertura nacional desde o dia 1
4. Transparência da metodologia (esta seção, versionada)

## Fontes (V1)

| Fonte | Origem | Ingestão |
|---|---|---|
| Portal da Transparência | api.portaldatransparencia.gov.br | API REST diária |
| Receita Federal CNPJ | dados.gov.br/dataset/cnpj | Download mensal + DuckDB |
| CEIS / CNEP | portaldatransparencia.gov.br/sancoes | CSV semanal |
| TSE Doações | dadosabertos.tse.jus.br | Download por eleição |
| Compras.gov.br | compras.dados.gov.br | API REST diária |
| IBGE | ibge.gov.br | CSV/Shapefile anual |
| Portais municipais (ERPs) | E&L, IPM, Betha, Equiplano | Scraper Python por ERP |

## Regras de alerta (V1)

Cada regra é versionada em código (`apps/etl/olho_publico_etl/alerts/rules/`) e levantada com semver (`versao_atual`).

### EMPRESA_FOGUETE — v1.0.0
**Lógica:** CNPJ aberto há <12 meses recebeu contrato >R$ 500.000.
**Severidade padrão:** forte.
**Fontes:** Receita Federal (data de abertura) + Portal da Transparência ou Compras.gov (contrato).

### DISPENSA_SUSPEITA — v1.0.0
**Lógica:** Contrato sem licitação (modalidade DISPENSA) acima de R$ 1.000.000.
**Severidade padrão:** atenção.

### SOCIO_SANCIONADO — v1.0.0
**Lógica:** Empresa cujo sócio aparece em CEIS ou CNEP firma novo contrato público.
**Severidade padrão:** forte.

### CRESCIMENTO_ANOMALO — v1.0.0
**Lógica:** Empresa cujo faturamento público total cresceu mais de 300% (>=4x) em relação ao ano anterior.
**Severidade padrão:** atenção.

### CONCENTRACAO — v1.0.0
**Lógica:** Mesma empresa concentra mais de 40% dos contratos de um órgão/secretaria em um ano.
**Severidade padrão:** informativo.

### DOADOR_BENEFICIADO — v1.0.0
**Lógica:** Empresa que doou para a campanha vitoriosa de prefeito recebe contrato da prefeitura após o início do mandato.
**Severidade padrão:** atenção.

## Disclaimer obrigatório

> "Este é um sinal automatizado baseado em dados públicos oficiais. Não constitui acusação ou conclusão investigativa."

## Direito de resposta

Toda página tem botão para contestar. Contestações procedentes são publicadas vinculadas ao registro original.
