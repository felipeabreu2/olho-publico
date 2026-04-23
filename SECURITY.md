# Política de Segurança

Obrigado por se preocupar com a segurança do Olho Público. Como este projeto trabalha com dados públicos brasileiros e expõe um portal acessado por cidadãos, levamos vulnerabilidades a sério.

## Versões suportadas

Como o projeto está em desenvolvimento ativo (V1 / MVP), apenas a branch `main` recebe correções de segurança.

| Versão | Suporte |
|---|---|
| `main` (HEAD) | ✅ Sim |
| Tags V1.x quando lançadas | ✅ Sim |
| Versões anteriores | ❌ Não |

## Como reportar uma vulnerabilidade

**Não abra uma issue pública para vulnerabilidades de segurança.** Isso pode expor os usuários antes que tenhamos tempo de corrigir.

Use um destes canais:

### 1. Private Vulnerability Reporting (preferido)

GitHub permite reportes privados diretamente no repositório:

👉 [**Reportar vulnerabilidade privadamente**](https://github.com/felipeabreu2/olho-publico/security/advisories/new)

Vantagens:
- Discussão criptografada com os mantenedores
- Histórico fica no próprio GitHub
- Após correção, vira CVE público com créditos

### 2. Email

Se não tem conta GitHub ou prefere email, escreva para:

📧 **security@olhopublico.org** (ou, enquanto domínio não está ativo, abra issue privada via canal acima)

Inclua na mensagem:
- Descrição da vulnerabilidade
- Passos para reproduzir
- Impacto potencial (qual dado ou recurso fica em risco)
- Sugestão de correção, se tiver
- Se você quer ser creditado publicamente após a correção

## O que esperar de nós

| Etapa | Prazo-alvo |
|---|---|
| Confirmar recebimento | até 3 dias úteis |
| Avaliação inicial e severidade | até 7 dias úteis |
| Correção em `main` | até 30 dias para severidade alta/crítica; melhor esforço para média/baixa |
| Disclosure público (CVE/advisory) | após correção em produção |

## Escopo

### O que está no escopo

- Vulnerabilidades em código deste repositório (web, ETL, schema)
- Configurações inseguras em `infra/` que possam ser exploradas
- Vazamento involuntário de dados pessoais (CPFs não mascarados, emails de contestação expostos etc.)
- XSS, SQL injection, SSRF, RCE, autenticação/autorização (quando V5+ existir)
- Vulnerabilidades em dependências (cobertas também por Dependabot)

### Fora do escopo

- Bugs de UI sem impacto de segurança (use issue normal)
- Falhas em sistemas oficiais brasileiros (Portal da Transparência, Receita etc.) — reporte direto ao órgão responsável
- Engenharia social, phishing contra mantenedores
- Ataques que requerem acesso físico ao servidor

## Boas práticas de quem reporta

- **Não tente acessar dados de outros usuários** ou explorar a vulnerabilidade além do necessário para demonstrá-la
- **Não execute ataques de negação de serviço (DoS)**
- **Não publique a vulnerabilidade** antes da correção
- **Atue de boa-fé** — pesquisadores que seguem essas regras não serão alvo de ação legal (compromisso de [Safe Harbor](https://disclose.io/) público)

## Segurança de dependências

Este repositório usa:
- **Dependabot alerts** — atualizações automáticas para `npm`, `pip`, `github-actions`, `docker` (ver [.github/dependabot.yml](.github/dependabot.yml))
- **CodeQL** — análise estática semanal (ver [.github/workflows/codeql.yml](.github/workflows/codeql.yml))
- **Secret scanning** — habilitado no GitHub (alerta se algum segredo vazar em commit)

## LGPD e dados pessoais

Se você descobriu um vazamento envolvendo **dados pessoais de cidadãos brasileiros**, por favor priorize o reporte como crítico. Iremos:
1. Conter o vazamento
2. Notificar a ANPD se houver risco a titulares (Lei 13.709/2018, Art. 48)
3. Comunicar pessoas afetadas quando aplicável
4. Publicar análise pública pós-incidente

---

Obrigado por ajudar a manter o Olho Público seguro para os cidadãos brasileiros.
