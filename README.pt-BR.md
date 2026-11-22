# Agentic Engineering Skills

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

Uma biblioteca gratuita e open source de workflows reutilizáveis de engenharia de software para agentes. Cada skill tem responsabilidade estreita, limites explícitos de ativação, comportamento seguro em falhas e instruções revisáveis. A fonte neutra em relação a fornecedores existe somente em `.agents/skills/`; OpenAI Codex é a plataforma prioritária.

Compatibilidade estrutural não comprova qualidade comportamental. O repositório valida arquivos e cenários offline, enquanto resultados de agentes reais são registrados separadamente e ainda estão pendentes.

## Catálogo de skills

- `api-design`: projeta ou evolui contratos de APIs e integrações.
- `code-review`: revisa mudanças em busca de defeitos acionáveis sustentados por evidências.
- `commits`: prepara, organiza, revisa ou cria commits Git focados.
- `debug`: investiga falhas observadas por meio de diagnósticos controlados.
- `deployment-readiness`: avalia a prontidão para implantação controlada sem implantar.
- `docs`: cria, revisa ou atualiza documentação técnica de software.
- `refactor`: melhora a manutenibilidade preservando o comportamento observável.
- `security-review`: realiza revisões defensivas de segurança autorizadas.
- `sql`: desenvolve e revisa SQL relacional e evolução segura de esquemas.
- `testing`: planeja, implementa, executa ou avalia testes automatizados.

Cada diretório canônico contém `SKILL.md` e, quando úteis, arquivos `references/` focados e carregados somente sob demanda.

## Início rápido

As ferramentas do repositório exigem Python 3.11 ou superior. O validador usa a dependência PyYAML fixada; o instalador e as demais ferramentas usam a biblioteca padrão.

```shell
git clone https://github.com/rodri-oliveira-dev/agentic-engineering-skills.git
cd agentic-engineering-skills
python -m venv .venv
```

Use o interpretador do ambiente virtual para instalar dependências e executar as validações.

Linux e macOS:

```shell
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/validate_skills.py --require-skills
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/evaluate_scenarios.py check
```

Windows PowerShell:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/validate_skills.py --require-skills
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe scripts/evaluate_scenarios.py check
```

Comandos de ativação pertencem às plataformas, não são opções de CLI deste repositório:

- **Codex:** use diretamente o catálogo `.agents/skills/` versionado ou copie diretórios completos das skills selecionadas para outro repositório. Consulte o [guia do Codex](docs/platforms/codex.md).
- **GitHub Copilot:** use o mesmo diretório canônico de projeto; a GitHub CLI também oferece um fluxo de instalação em prévia pública. Consulte o [guia do Copilot](docs/platforms/github-copilot.md).
- **Claude Code:** visualize e crie uma distribuição gerenciada em `.claude/skills/` com o instalador incluído:

  ```shell
  python scripts/install_skills.py --platform claude-code --destination .claude/skills --all --dry-run
  python scripts/install_skills.py --platform claude-code --destination .claude/skills --all
  ```

  Consulte o [guia do Claude Code](docs/platforms/claude-code.md) antes de escolher um destino explícito de projeto ou usuário.

## Atualização

Atualize este checkout com Git somente depois de preservar ou registrar o trabalho local e execute novamente as validações. Codex e Copilot usam este repositório imediatamente ao operar nele. Para uma instalação gerenciada do Claude Code, repita o mesmo comando do instalador; ele atualiza arquivos gerenciados não alterados e recusa sobrescrever conteúdo não gerenciado ou modificado localmente. Cópias manuais precisam ser revisadas e substituídas manualmente.

## Validação e compatibilidade

As verificações automatizadas cobrem estrutura e metadados das dez skills, referências locais seguras, integridade do catálogo, instalação, atualização e remoção, prevenção de sobrescrita, entradas inválidas, regressões do validador, cobertura de cenários e links da documentação. Elas não exigem credenciais, serviços pagos nem rede e nunca executam comandos das skills.

Descoberta, ativação, recusa e qualidade de saída em modelos reais constituem evidência diferente. Consulte [Validação e testes](docs/validation.md), a [matriz de compatibilidade](docs/platforms/compatibility-matrix.md) e a [prontidão da v1.0.0](docs/releases/v1.0.0-readiness.md) para conhecer os limites exatos.

## Contribuição e segurança

Leia [Como contribuir](CONTRIBUTING.md) e o [contrato de autoria de skills](docs/skill-authoring.md), adicione testes focados e informe somente verificações realmente executadas. Relate vulnerabilidades de forma privada conforme a [política de segurança](SECURITY.md). O projeto usa a [licença MIT](LICENSE); dependências e atribuições conhecidas estão nos [avisos de terceiros](THIRD_PARTY_NOTICES.md).

Documentação adicional: [arquitetura](docs/architecture.md), [roadmap](docs/roadmap.md) e [guias de plataforma](docs/platforms/compatibility-matrix.md).
