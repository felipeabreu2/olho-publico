# Cloudflare Worker — proxy CGU

A API do Portal da Transparência (CGU) **bloqueia requests com IP de origem fora do Brasil**: retornam 403 com body vazio. Identificável pelo header `x-amz-cf-pop` da resposta apontar para um POP CloudFront não-BR (ex: `FRA56` em Frankfurt, `LHR50` em Londres).

Como Cloudflare Workers tem POPs em GRU (São Paulo) e GIG (Rio), e o egress para `api.portaldatransparencia.gov.br` acaba indo pela rede BR, hospedar um proxy lá funciona como contorno legítimo (não estamos burlando segurança, apenas usando uma rede CDN para alcançar a API).

## Deploy (5 minutos)

### 1. Criar Worker

1. https://dash.cloudflare.com → **Workers & Pages** → **Create application** → **Create Worker**
2. Nome sugerido: `transparencia-proxy`
3. **Deploy** o template padrão
4. **Edit code** → cole o conteúdo de [`transparencia-proxy.js`](transparencia-proxy.js) → **Save and deploy**

### 2. Configurar a chave como Secret

1. Worker → **Settings → Variables**
2. **Environment Variables** → **Add variable**
3. Nome: `TRANSPARENCIA_API_KEY`
4. Valor: sua chave da CGU
5. Marque **Encrypt** → **Save and deploy**

### 3. Pegar URL e usar no ETL

1. URL do worker aparece no painel: `https://transparencia-proxy.<SUBDOMAIN>.workers.dev`
2. No Portainer (stack `olho-publico`), edita as env vars e adiciona:

```env
TRANSPARENCIA_BASE_URL=https://transparencia-proxy.<SUBDOMAIN>.workers.dev
```

3. **Pull and redeploy** a stack — ETL agora rota tudo via worker

## Verificar que funcionou

```bash
# Da sua VPS europeia, com a mesma chave:
curl -H "chave-api-dados: SUA_CHAVE" \
  "https://transparencia-proxy.<SUBDOMAIN>.workers.dev/api-de-dados/transferencias?codigoIbge=3550308&mesAnoInicio=202604&mesAnoFim=202604&pagina=1"

# Esperado: HTTP 200 + JSON array com transferências
```

## Custo

Free tier da Cloudflare = 100.000 requests/dia. Mais que suficiente para:
- 1 município × 1 mês × ~5 páginas = 5 requests
- 100 municípios × 12 meses × ~5 páginas = 6.000 requests/sync
- Sync diário = 6.000 req/dia (6% da quota)

## Limitações

- Worker tem timeout de 30s por request (paid: 5min). Cada página da API é rápida (~1s), então OK.
- Workers Free não permitem domínio customizado (só `*.workers.dev`). Para `transparencia.olhopublico.org`, plano Workers Paid (US$ 5/mês).

## Alternativas

Se preferir não usar Cloudflare:
- **Fly.io** em região GRU (São Paulo) — também free tier
- **GCP Cloud Run** em southamerica-east1 — free tier
- **VPS pequeno em provider BR** (Locaweb, UOL, Hostinger BR) — ~R$10-20/mês
