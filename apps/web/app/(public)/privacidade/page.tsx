export const metadata = { title: "Política de privacidade" };

export default function PrivacidadePage() {
  return (
    <article className="mx-auto max-w-3xl px-4 py-12 prose prose-invert">
      <h1>Política de privacidade</h1>
      <p>Última atualização: 22/04/2026.</p>

      <h2>Resumo</h2>
      <ul>
        <li>O Olho Público <strong>não exige cadastro</strong> para navegação.</li>
        <li>Não usamos cookies de tracking nem identificadores publicitários.</li>
        <li>Analytics privacy-first: contagem agregada de visitas, sem identificação pessoal.</li>
        <li>Dados pessoais coletados: apenas email, opcional, em formulários de contestação.</li>
      </ul>

      <h2>Dados sobre terceiros</h2>
      <p>
        Exibimos dados públicos oficiais brasileiros (LAI — Lei 12.527/2011). CPFs aparecem
        sempre mascarados (ex: <code>***.123.456-**</code>) quando vinculados a doações ou sociedades.
        Razão social e dados cadastrais de empresas vêm da Receita Federal.
      </p>

      <h2>Direitos do titular (LGPD)</h2>
      <p>
        Para qualquer solicitação relacionada a dados pessoais, escreva para{" "}
        <a href="mailto:lgpd@olhopublico.org">lgpd@olhopublico.org</a>.
      </p>
    </article>
  );
}
