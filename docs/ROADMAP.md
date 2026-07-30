# Roadmap

## Princípios

- Preservar o comportamento funcional durante a modernização.
- Fazer mudanças pequenas, verificáveis e reversíveis.
- Tratar segurança de credenciais antes de distribuir novos builds.
- Manter uma única fonte oficial para código, build e instalador.

## Sprint 1 — organização da base

- Criar a branch `develop`.
- Centralizar documentação em `docs/`.
- Adotar um `.gitignore` adequado ao projeto.
- Classificar diretórios oficiais, legados e candidatos a arquivamento.
- Não alterar regras de negócio, build, instalador ou credenciais.

## Sprint 2 — segurança de configuração

- Externalizar credenciais para diretório gravável fora do bundle.
- Remover credenciais do versionamento e dos artefatos de distribuição.
- Criar diagnóstico claro para configuração ausente.
- Permitir substituição de credenciais sem recompilação.

## Sprint 3 — consolidação estrutural

- Validar e arquivar cópias históricas.
- Eliminar duplicações comprovadas.
- Definir contratos entre interface, serviços e integrações.
- Introduzir testes de caracterização antes de refatorar.

## Sprint 4 — qualidade e automação

- Automatizar testes, lint e validações de build.
- Padronizar versionamento e changelog.
- Medir desempenho da geração e impressão de crachás.
- Documentar operação, suporte e recuperação de falhas.
