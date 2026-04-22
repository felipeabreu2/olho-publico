import type { MetadataRoute } from "next";
import { mockMunicipios } from "@/lib/mock";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

  const cityUrls = mockMunicipios.map((m) => ({
    url: `${base}/cidade/${m.uf}/${m.slug}`,
    lastModified: new Date(),
    changeFrequency: "daily" as const,
    priority: 0.8,
  }));

  return [
    { url: base, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
    { url: `${base}/metodologia`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.5 },
    { url: `${base}/privacidade`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    ...cityUrls,
  ];
}
