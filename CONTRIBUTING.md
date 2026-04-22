# Como contribuir

Olho Público é um projeto cívico aberto a contribuições de jornalistas, devs, designers e qualquer pessoa preocupada com transparência pública.

## Tipos de contribuição valiosa

- **Scrapers de prefeitura** — investigar portais municipais e implementar (ou melhorar) scrapers para os 4 ERPs principais (E&L, IPM, Betha, Equiplano)
- **Regras de alerta** — propor novas regras de detecção (em `apps/etl/olho_publico_etl/alerts/rules/`) sempre acompanhadas de testes e documentação metodológica
- **UI/UX** — melhorias no front, em particular acessibilidade e mobile
- **Documentação** — explicações em linguagem simples na metodologia

## Processo

1. Abra uma issue descrevendo o que pretende
2. Fork → branch (`feat/nome-curto`) → PR
3. PR precisa passar em CI (`pnpm test`, `pytest`, lint, typecheck)
4. Toda nova regra de alerta exige:
   - Teste unitário com fixtures
   - Atualização em `docs/METODOLOGIA.md`
   - Bump de `versao_atual` se mudar comportamento

## Estilo de código

- TypeScript strict; eslint configurado em `apps/web`
- Python ruff + mypy em `apps/etl`
- Commits em português, padrão `tipo(escopo): mensagem` (`feat(web):`, `fix(etl):`, `docs:`)

## Boas práticas com dados públicos

- Toda nova fonte deve gravar **raw** original no R2 antes de qualquer parsing
- CPFs sempre mascarados (use `mask_cpf` de `utils/cpf_mask.py`)
- Disclaimers obrigatórios em qualquer regra de alerta
