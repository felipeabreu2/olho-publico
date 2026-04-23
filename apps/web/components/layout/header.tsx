import Link from "next/link";
import { Eye } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-md bg-bg/80 border-b border-border-subtle">
      <div className="mx-auto max-w-6xl px-4 py-3.5 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fg/40 rounded"
        >
          <div className="size-7 rounded-md bg-fg/10 flex items-center justify-center transition-colors group-hover:bg-fg/15">
            <Eye className="size-4 text-fg" strokeWidth={2.25} />
          </div>
          <span className="font-semibold tracking-tight text-fg">
            Olho Público
          </span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {[
            { href: "/busca", label: "Busca" },
            { href: "/metodologia", label: "Metodologia" },
            { href: "/contestar", label: "Contestar dado" },
          ].map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="px-3 py-1.5 rounded-md text-fg-muted hover:text-fg hover:bg-bg-elevated transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fg/40"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
