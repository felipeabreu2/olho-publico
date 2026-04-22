import Link from "next/link";
import { Eye } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-border-subtle">
      <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Eye className="size-5 text-fg" />
          <span className="font-semibold tracking-tight">Olho Público</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm text-fg-muted">
          <Link href="/busca" className="hover:text-fg">Busca</Link>
          <Link href="/metodologia" className="hover:text-fg">Metodologia</Link>
          <Link href="/contestar" className="hover:text-fg">Contestar dado</Link>
        </nav>
      </div>
    </header>
  );
}
