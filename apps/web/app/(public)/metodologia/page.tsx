import Link from "next/link";

export const metadata = { title: "Metodologia" };

export default function MetodologiaPage() {
  return (
    <article className="mx-auto max-w-3xl px-4 py-12 prose prose-invert">
      <h1>Metodologia</h1>

      <h2>Princípios</h2>
      <ul>
        <li><strong>Fato antes de opinião</strong> — só dados oficiais agregados.</li>
        <li><strong>Sinais não são acusações</strong> — alertas levam disclaimer e link para evidência.</li>
        <li><strong>Cobertura nacional</strong> — qualquer das 5.570 cidades pode ser consultada.</li>
        <li><strong>Transparência</strong> — toda regra é versionada em código aberto.</li>
      </ul>

      <h2>Fontes</h2>
      <ul>
        <li><strong>Portal da Transparência (CGU)</strong> — contratos, convênios, transferências federais.</li>
        <li><strong>Receita Federal</strong> — base CNPJ (empresas e sócios).</li>
        <li><strong>CEIS / CNEP (CGU)</strong> — empresas inidôneas e sancionadas.</li>
        <li><strong>TSE</strong> — doações eleitorais.</li>
        <li><strong>Compras.gov.br</strong> — licitações federais.</li>
        <li><strong>IBGE</strong> — municípios, população, IDH.</li>
        <li><strong>Portais municipais (via ERPs)</strong> — contratos e licitações de prefeituras.</li>
      </ul>

      <h2>Regras de alerta</h2>
      <p>Cada regra tem um identificador, parâmetros documentados e disclaimer obrigatório.</p>
      <h3 id="empresa-foguete">EMPRESA_FOGUETE</h3>
      <p>CNPJ aberto há &lt;12 meses recebeu contrato &gt; R$ 500 mil. <em>Severidade padrão: forte.</em></p>
      <h3 id="dispensa-suspeita">DISPENSA_SUSPEITA</h3>
      <p>Contrato sem licitação acima de R$ 1 milhão. <em>Severidade padrão: atenção.</em></p>
      <h3 id="socio-sancionado">SOCIO_SANCIONADO</h3>
      <p>Empresa com contrato cujo sócio aparece em CEIS/CNEP. <em>Severidade padrão: forte.</em></p>
      <h3 id="crescimento-anomalo">CRESCIMENTO_ANOMALO</h3>
      <p>Empresa cujo faturamento público cresceu &gt;300% ano a ano. <em>Severidade padrão: atenção.</em></p>
      <h3 id="concentracao">CONCENTRACAO</h3>
      <p>Mesma empresa = &gt;40% dos contratos de uma secretaria. <em>Severidade padrão: informativo.</em></p>
      <h3 id="doador-beneficiado">DOADOR_BENEFICIADO</h3>
      <p>Empresa que doou para campanha do prefeito atual recebeu contrato após eleição. <em>Severidade padrão: atenção.</em></p>

      <h2>Direito de resposta</h2>
      <p>
        Encontrou um dado que considera incorreto ou descontextualizado?
        Use a <Link href="/contestar">página de contestação</Link>. Toda contestação procedente é
        publicada vinculada ao registro original.
      </p>

      <h2>Código aberto e auditabilidade</h2>
      <p>O código-fonte e todas as regras são públicos sob licença source-available.</p>
    </article>
  );
}
