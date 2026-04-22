import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: {
    default: "Olho Público — para onde vai o dinheiro público brasileiro",
    template: "%s · Olho Público",
  },
  description:
    "Plataforma pública e aberta que mostra como o dinheiro público é gasto na sua cidade.",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
  openGraph: {
    locale: "pt_BR",
    type: "website",
    siteName: "Olho Público",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
