# Agentic Engineering Skills

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

Agentic Engineering Skills é uma coleção gratuita e open source de skills reutilizáveis para agentes de engenharia de software. O projeto pretende transformar práticas recorrentes de engenharia em instruções revisáveis e versionadas, sem vincular seu conteúdo central a um único fornecedor.

A biblioteca trata um problema comum: workflows de agentes costumam ser repetidos em prompts, ficar espalhados entre repositórios ou ser escritos em formatos específicos de uma plataforma. Este repositório oferece skills focadas, com escopo, entradas, workflow, validação e tratamento de falhas explícitos.

## Público-alvo

O projeto é destinado a pessoas desenvolvedoras, mantenedoras e equipes que desejam inspecionar, adaptar e compartilhar workflows repetíveis para agentes.

## Suporte a plataformas

O contrato compartilhado segue a [especificação aberta Agent Skills](https://agentskills.io/specification), e `.agents/skills/` é a única fonte canônica.

- **OpenAI Codex:** o catálogo com dez skills está implementado no local de descoberta do repositório usado pelo Codex e foi validado estruturalmente. Os cenários comportamentais representativos estão documentados, mas ainda não houve avaliação comportamental automatizada entre modelos.
- **GitHub Copilot:** o catálogo canônico usa o local de projeto `.agents/skills/` documentado pelo Copilot e teve sua compatibilidade estrutural verificada. A descoberta, a ativação e a execução dos workflows ainda não foram verificadas comportamentalmente nas diferentes superfícies do Copilot.
- **Claude Code:** o catálogo canônico corresponde ao formato Agent Skills aceito pelo Claude Code e pode ser instalado como uma distribuição gerada, gerenciada por hashes, em `.claude/skills/`. A descoberta, a ativação e a execução dos workflows ainda não foram verificadas comportamentalmente no Claude Code.

Integrações específicas de plataforma deverão reutilizar a fonte canônica, sem manter cópias editáveis independentes.

## Princípios de qualidade

- Uma responsabilidade bem definida por skill.
- Instruções concisas e orientadas a ações, com carregamento progressivo de referências.
- Validação observável, sem inventar resultados de testes, diagnósticos ou verificações.
- Tratamento explícito de pré-condições, incertezas, falhas e limitações.
- Confirmação antes de operações destrutivas ou irreversíveis.
- Respeito às permissões e políticas de segurança do ambiente.
- Núcleo portável, separado de extensões específicas de fornecedores.

## Documentação

- [Arquitetura](docs/architecture.md)
- [Contrato para autoria de skills](docs/skill-authoring.md)
- [Validação e testes](docs/validation.md)
- [GitHub Copilot](docs/platforms/github-copilot.md)
- [Claude Code](docs/platforms/claude-code.md)
- [Matriz de compatibilidade entre plataformas](docs/platforms/compatibility-matrix.md)
- [Roadmap](docs/roadmap.md)
- [Como contribuir](CONTRIBUTING.md)
- [README principal em inglês](README.md)

## Catálogo de skills

As skills canônicas ficam em [`.agents/skills/`](.agents/skills/). O catálogo planejado completo contém atualmente dez skills implementadas:

- `docs`: cria, revisa e atualiza documentação técnica de software.
- `commits`: prepara, organiza, revisa e cria commits Git focados.
- `refactor`: melhora a manutenibilidade preservando o comportamento observável.
- `api-design`: projeta e evolui contratos de APIs e integrações.
- `testing`: planeja, implementa, executa e avalia testes automatizados.
- `code-review`: revisa diffs e mudanças propostas em busca de defeitos acionáveis sustentados por evidências.
- `sql`: desenvolve e revisa SQL relacional, integridade, transações, índices e evolução segura de esquemas.
- `debug`: investiga falhas observadas com evidências, hipóteses verificáveis e diagnósticos controlados.
- `security-review`: realiza revisões defensivas autorizadas de código, configuração, dependências e arquitetura.
- `deployment-readiness`: avalia a prontidão técnica para implantação controlada sem executá-la.

Cada skill possui um único `SKILL.md` canônico; orientações especializadas ficam em arquivos `references/` carregados sob demanda, e cenários representativos positivos, negativos e de evidência insuficiente ficam em `tests/fixtures/<skill>/`. Consulte o [guia do GitHub Copilot](docs/platforms/github-copilot.md), o [guia do Claude Code](docs/platforms/claude-code.md) e o [roadmap](docs/roadmap.md) para instalação, evidência estrutural, avaliação comportamental e o trabalho restante de plataformas.

## Estado do projeto

A fundação e todas as dez skills planejadas estão implementadas. Isso não representa uma versão 1.0 publicada. O Copilot não precisa de adaptador de projeto porque reconhece o diretório canônico. Um instalador Python baseado apenas na biblioteca padrão gera distribuições gerenciadas para o Claude Code sem alterar as skills canônicas. A avaliação comportamental automatizada ainda não está disponível.

Com Python 3.11 ou superior e as dependências de `requirements.txt` instaladas, execute `python scripts/validate_skills.py --require-skills` para validar o catálogo não vazio e `python -m unittest discover -s tests -v` para rodar os testes automatizados do validador. A validação estrutural verifica formato, metadados, integridade do catálogo e referências locais; ela não demonstra ativação ou qualidade comportamental das skills. Cenários comportamentais representativos estão documentados em `tests/fixtures/`, mas não constituem resultados de testes automatizados.

O desenvolvimento é público, e o projeto é software livre distribuído sob a [licença MIT](LICENSE).
