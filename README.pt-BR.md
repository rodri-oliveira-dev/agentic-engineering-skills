# Agentic Engineering Skills

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

Agentic Engineering Skills é uma coleção gratuita e open source de skills reutilizáveis para agentes de engenharia de software. O projeto pretende transformar práticas recorrentes de engenharia em instruções revisáveis e versionadas, sem vincular seu conteúdo central a um único fornecedor.

A biblioteca trata um problema comum: workflows de agentes costumam ser repetidos em prompts, ficar espalhados entre repositórios ou ser escritos em formatos específicos de uma plataforma. Este repositório oferecerá skills focadas, com escopo, entradas, workflow, validação e tratamento de falhas explícitos.

## Público-alvo

O projeto é destinado a pessoas desenvolvedoras, mantenedoras e equipes que desejam inspecionar, adaptar e compartilhar workflows repetíveis para agentes.

## Plataformas planejadas

O desenvolvimento priorizará:

1. OpenAI Codex
2. GitHub Copilot
3. Claude Code

O contrato compartilhado segue a [especificação aberta Agent Skills](https://agentskills.io/specification). O suporte a cada plataforma só será declarado depois de implementado e testado. A fonte canônica ficará em `.agents/skills/`; integrações específicas deverão reutilizá-la, sem manter cópias independentes.

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
- [Roadmap](docs/roadmap.md)
- [Como contribuir](CONTRIBUTING.md)
- [README principal em inglês](README.md)

## Estado do projeto

O projeto está na fase de fundação. A arquitetura, o contrato de autoria, a validação estrutural, o workflow de CI e as orientações de contribuição estão estabelecidos; nenhuma das dez skills planejadas foi implementada. Instaladores, adaptadores de plataforma e avaliação comportamental ainda não estão disponíveis.

Com Python 3.11 ou superior e as dependências de `requirements.txt` instaladas, execute `python scripts/validate_skills.py` para validar o catálogo e `python -m unittest discover -s tests -v` para rodar a suíte. Um catálogo vazio é permitido durante a fundação e é informado como zero skills validadas.

O desenvolvimento é público, e o projeto é software livre distribuído sob a [licença MIT](LICENSE).
