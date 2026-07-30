# Arquitetura do SistemaCrachaCDN

## Objetivo

O SistemaCrachaCDN é uma aplicação desktop Python para consultar dados de colaboradores, obter ou capturar fotografias, gerar crachás com QR Code e enviar o resultado para impressão.

Esta documentação descreve o estado atual. A Sprint 1 não altera regras de negócio, build, instalador ou credenciais.

## Componentes oficiais

- `app/`: pacote principal da aplicação.
- `app/ui/`: interface gráfica ativa e orquestração das ações do usuário.
- `app/vision/`: automação e reconhecimento usados na integração SisWeb.
- `config/`: configurações da aplicação e das integrações.
- `templates/`: modelos visuais dos crachás.
- `fonts/`: fontes usadas na composição gráfica.
- `models/`: modelos e artefatos de visão computacional.
- `installer/`: fonte oficial do instalador Inno Setup.
- `SistemaCrachaCDN.spec`: configuração oficial do PyInstaller.
- scripts `.bat` da raiz: fluxo oficial de geração de executável e instalador.

## Fluxo de execução

1. A aplicação é iniciada pelo ponto de entrada Python ou pelo executável empacotado.
2. O gerenciador de caminhos resolve recursos para execução em código-fonte ou em bundle PyInstaller.
3. A interface carrega configurações e serviços.
4. O operador pesquisa ou informa os dados do colaborador.
5. As integrações Google Sheets e SisWeb fornecem ou complementam dados e fotografia.
6. O gerador compõe frente e verso do crachá a partir dos templates.
7. O QR Code é gerado e incorporado ao layout.
8. O arquivo final é salvo e encaminhado ao fluxo de impressão.
9. A integração Google Drive pode armazenar ou recuperar recursos conforme a operação configurada.

## Limites arquiteturais atuais

A interface ainda concentra parte relevante da orquestração. Há cópias históricas de UI, build, instalador e SisWeb no repositório; elas não devem ser consideradas fontes oficiais. A classificação completa está em [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

## Empacotamento

O build oficial é baseado em PyInstaller e no arquivo `SistemaCrachaCDN.spec`. O instalador oficial é produzido pelo Inno Setup a partir de `installer/`. Consulte [BUILD.md](BUILD.md) antes de alterar esse fluxo.
