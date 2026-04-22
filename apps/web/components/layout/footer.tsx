import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border-subtle mt-16">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-fg-muted flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
        <div>
          <p className="text-fg font-medium">Olho Público</p>
          <p className="mt-1">
            Plataforma cívica baseada em dados oficiais. Sem opiniões — só fatos e sinais documentados.
          </p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link href="/metodologia" className="hover:text-fg">Metodologia</Link>
          <Link href="/privacidade" className="hover:text-fg">Privacidade</Link>
          <Link href="/contestar" className="hover:text-fg">Contestar dado</Link>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-fg">
            Código (GitHub)
          </a>
        </div>
      </div>
    </footer>
  );
}
