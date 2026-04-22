import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export const metadata = { title: "Contestar dado" };

export default function ContestarPage() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-3xl font-bold mb-2">Contestar dado</h1>
      <p className="text-fg-muted mb-8">
        Encontrou um dado que considera incorreto ou descontextualizado? Conte para a gente.
        Após análise, a resposta fica vinculada ao registro original.
      </p>

      <Card>
        <CardHeader>
          <CardTitle>Formulário</CardTitle>
          <CardDescription>
            Sua mensagem entra em fila de moderação. Em V1 ainda não há envio automático — utilize o email abaixo.
          </CardDescription>
        </CardHeader>
        <form className="space-y-4">
          <div>
            <label className="block text-sm text-fg-muted mb-1">Seu email</label>
            <Input type="email" placeholder="voce@exemplo.com" />
          </div>
          <div>
            <label className="block text-sm text-fg-muted mb-1">Link da página contestada</label>
            <Input type="url" placeholder="https://olhopublico.org/cidade/..." />
          </div>
          <div>
            <label className="block text-sm text-fg-muted mb-1">Mensagem</label>
            <textarea
              className="w-full rounded-md border border-border bg-bg-elevated px-3 py-2 text-sm text-fg min-h-32"
              placeholder="Descreva o que parece incorreto e, se possível, indique a fonte oficial divergente."
            />
          </div>
          <Button type="button" disabled>
            Enviar (em construção)
          </Button>
        </form>
        <p className="mt-4 text-sm text-fg-subtle">
          Por ora, envie para{" "}
          <a className="underline" href="mailto:contato@olhopublico.org">
            contato@olhopublico.org
          </a>
          .
        </p>
      </Card>
    </div>
  );
}
