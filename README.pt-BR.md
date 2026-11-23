# Agentic Engineering Skills

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

Uma biblioteca gratuita e open source de dez workflows reutilizáveis de engenharia de software para agentes. A fonte canônica e neutra em relação a fornecedores existe somente em `.agents/skills/`; os pacotes gerados para marketplaces derivam dela. OpenAI Codex é a plataforma prioritária.

A versão [`1.0.0`](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/releases/tag/1.0.0) está publicada. Publicação e validação estrutural não comprovam comportamento em agentes reais; consulte o [registro de publicação](docs/releases/1.0.0-publication.md) para conhecer as evidências e limitações restantes.

## Instalação rápida

A CLI multiplataforma `skills` pode listar o catálogo sem instalá-lo:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --list
```

Instale uma skill e selecione interativamente os agentes de destino:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --skill code-review
```

Instale as dez skills para todos os agentes detectados somente depois de revisar a fonte e os destinos:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --all
```

Essa opção exige Node.js com `npx`, não Python. Para seleção explícita de agentes, instalação por marketplace, atualizações, remoção, cópias independentes e status verificado, use o [guia de instalação e distribuição](docs/distribution.md).

## Agentes e métodos de distribuição compatíveis

| Método | O que está disponível | Status verificado |
| --- | --- | --- |
| `npx skills` universal | Uma skill, skills selecionadas ou todas as skills para agentes selecionados | Listagem local e remota do catálogo validada com a CLI `1.9.0`; instalação com alterações não está registrada |
| Marketplace do OpenAI Codex | Plugin completo `agentic-engineering` | Registro do repositório público, listagem e instalação isolada validados com Codex CLI `0.171.0-alpha.13`; ativação real não testada |
| Marketplace da GitHub Copilot CLI | Plugin completo | Publicado e validado estruturalmente; instalação pela CLI e comportamento não testados |
| Marketplace do Claude Code | Plugin completo | Publicado e validado estruturalmente; instalação pela CLI e comportamento não testados |
| Instalação independente no projeto | `.agents/skills/` canônico para Codex/Copilot; cópia gerenciada em `.claude/skills/` para Claude Code | Estrutura do repositório e instalador do Claude testados sem iniciar um agente |

Os três manifests de marketplace estão publicamente disponíveis em `main`. A existência de um manifest significa **publicado**, verificações do repositório podem significar **validado estruturalmente**, uma operação de cliente bem-sucedida significa **instalação validada**, e uma execução controlada em agente real é necessária para **validação comportamental**. Não deduza um estado a partir de outro.

Guias de plataforma: [Codex](docs/platforms/codex.md), [GitHub Copilot](docs/platforms/github-copilot.md), [Claude Code](docs/platforms/claude-code.md) e [matriz de compatibilidade](docs/platforms/compatibility-matrix.md).

## Catálogo de skills

- [`api-design`](.agents/skills/api-design/SKILL.md): projeta ou evolui contratos de APIs e integrações.
- [`code-review`](.agents/skills/code-review/SKILL.md): revisa mudanças em busca de defeitos acionáveis sustentados por evidências.
- [`commits`](.agents/skills/commits/SKILL.md): prepara, organiza, revisa ou cria commits Git focados.
- [`debug`](.agents/skills/debug/SKILL.md): investiga falhas observadas por meio de diagnósticos controlados.
- [`deployment-readiness`](.agents/skills/deployment-readiness/SKILL.md): avalia a prontidão para implantação controlada sem implantar.
- [`docs`](.agents/skills/docs/SKILL.md): cria, revisa ou atualiza documentação técnica de software.
- [`refactor`](.agents/skills/refactor/SKILL.md): melhora a manutenibilidade preservando o comportamento observável.
- [`security-review`](.agents/skills/security-review/SKILL.md): realiza revisões defensivas de segurança autorizadas.
- [`sql`](.agents/skills/sql/SKILL.md): desenvolve e revisa SQL relacional e evolução segura de esquemas.
- [`testing`](.agents/skills/testing/SKILL.md): planeja, implementa, executa ou avalia testes automatizados.

Cada diretório canônico contém `SKILL.md` e, quando úteis, arquivos `references/` focados e carregados somente quando necessário.

## Compatibilidade e validação de plataformas

As verificações automatizadas cobrem estrutura, metadados, referências locais, integridade do catálogo, segurança do instalador, geração determinística de pacotes, hashes incorporados, cobertura de cenários e links da documentação. Elas não executam instruções das skills nem avaliam saídas de modelos. Atualmente, o repositório não contém nenhum registro concluído de avaliação comportamental.

Consulte [Validação e testes](docs/validation.md), a [matriz de compatibilidade](docs/platforms/compatibility-matrix.md), a avaliação histórica de [prontidão da v1.0.0](docs/releases/v1.0.0-readiness.md) e o registro factual de [publicação da v1.0.0](docs/releases/1.0.0-publication.md).

## Desenvolvimento e testes

Python 3.11 ou superior e a dependência PyYAML fixada são necessários para desenvolver e validar este repositório; eles não são requisitos para todos os métodos de instalação.

Linux e macOS:

```shell
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_skills.py --require-skills
.venv/bin/python scripts/evaluate_scenarios.py check
.venv/bin/python scripts/package_plugins.py check
.venv/bin/python scripts/package_plugins.py verify
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe scripts\validate_skills.py --require-skills
.venv\Scripts\python.exe scripts\evaluate_scenarios.py check
.venv\Scripts\python.exe scripts\package_plugins.py check
.venv\Scripts\python.exe scripts\package_plugins.py verify
```

Edite somente `.agents/skills/`. Regenere a saída de marketplace apenas quando o conteúdo canônico das skills ou os metadados do pacote mudarem; alterações somente em documentação não exigem regeneração. Consulte a [arquitetura de distribuição de plugins](docs/distribution-architecture.md).

## Contribuição e segurança

Leia [Como contribuir](CONTRIBUTING.md) e o [contrato de autoria de skills](docs/skill-authoring.md), adicione evidências focadas e informe somente verificações realmente executadas. Relate vulnerabilidades de forma privada conforme a [política de segurança](SECURITY.md).

## Licença e documentação adicional

O projeto usa a [licença MIT](LICENSE). Dependências e atribuições conhecidas estão nos [avisos de terceiros](THIRD_PARTY_NOTICES.md). A documentação adicional inclui [arquitetura](docs/architecture.md), [roadmap](docs/roadmap.md) e [arquitetura de distribuição](docs/distribution-architecture.md).
