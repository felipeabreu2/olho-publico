"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export function SearchBar({ size = "lg" }: { size?: "md" | "lg" }) {
  const router = useRouter();
  const [q, setQ] = useState("");

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (q.trim()) router.push(`/busca?q=${encodeURIComponent(q.trim())}`);
  }

  const inputClass = size === "lg" ? "h-14 text-lg px-4" : "";

  return (
    <form onSubmit={onSubmit} className="flex gap-2 w-full max-w-2xl mx-auto">
      <Input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Digite sua cidade ou um CNPJ"
        className={inputClass}
        aria-label="Buscar cidade ou empresa"
      />
      <Button type="submit" size={size === "lg" ? "lg" : "md"}>
        <Search className="size-4 mr-2" /> Buscar
      </Button>
    </form>
  );
}
