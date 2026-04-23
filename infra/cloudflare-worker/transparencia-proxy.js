/**
 * Cloudflare Worker — proxy para api.portaldatransparencia.gov.br
 *
 * Por que: a API da CGU bloqueia requisições que chegam por edges CloudFront
 * fora do Brasil (proteção anti-scraping internacional). Quando o seu ETL
 * roda em VPS europeu/americano, todo request retorna 403 com body vazio.
 *
 * Workers da Cloudflare têm POPs no Brasil (GRU/GIG) e o egress para a
 * origem da CGU acaba pela rede BR — passando pela proteção.
 *
 * Deploy:
 *   1. Cloudflare Dashboard → Workers & Pages → Create Worker
 *   2. Cole este código
 *   3. Settings → Variables → adiciona secret TRANSPARENCIA_API_KEY
 *      (mesma chave da CGU; o worker valida)
 *   4. Deploy → pega URL workers.dev
 *   5. No Portainer (stack olho-publico), define:
 *        TRANSPARENCIA_BASE_URL=https://transparencia-proxy.SEU.workers.dev
 *
 * Custo: free tier dá 100k requests/dia (suficiente para syncs diários
 * de centenas de cidades).
 */

const TARGET_HOST = "api.portaldatransparencia.gov.br";

export default {
  async fetch(request, env) {
    // Anti-abuse: só aceita requests com a chave correta da CGU
    const incomingKey = request.headers.get("chave-api-dados");
    if (!env.TRANSPARENCIA_API_KEY || incomingKey !== env.TRANSPARENCIA_API_KEY) {
      return new Response(
        JSON.stringify({ error: "missing or invalid chave-api-dados" }),
        { status: 403, headers: { "content-type": "application/json" } },
      );
    }

    const incomingUrl = new URL(request.url);
    const targetUrl = new URL(
      incomingUrl.pathname + incomingUrl.search,
      `https://${TARGET_HOST}`,
    );

    // Reusa headers, mas força o Host correto
    const headers = new Headers(request.headers);
    headers.set("host", TARGET_HOST);

    const upstream = await fetch(targetUrl.toString(), {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
      redirect: "manual",
      cf: { cacheEverything: false },
    });

    // Repassa status, headers e body
    return new Response(upstream.body, {
      status: upstream.status,
      headers: upstream.headers,
    });
  },
};
