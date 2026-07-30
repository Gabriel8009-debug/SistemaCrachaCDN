# Build e instalação

Este documento descreve o fluxo atual. A Sprint 1 não modifica scripts, especificações ou instalador.

## Pré-requisitos

- Windows.
- Python e dependências instaladas em ambiente virtual.
- PyInstaller para gerar o executável.
- Inno Setup para gerar o instalador.

## Fonte oficial do executável

- Especificação: `SistemaCrachaCDN.spec`.
- Scripts oficiais na raiz: `GERAR_EXE_DEFINITIVO.bat`, `GERAR_INSTALADOR.bat` e `GERAR_TUDO.bat`.
- Saídas esperadas: `build/`, `dist/` e `dist_instalador/`.

## Fonte oficial do instalador

O diretório `installer/` contém a definição oficial do Inno Setup. `SistemaCracha_Instalador_Arquivos/` é uma cópia histórica e não deve ser usado como fonte canônica.

## Cuidados

- Execute os scripts a partir da raiz.
- Não use cópias legadas para produzir releases.
- Confirme recursos, caminhos e dependências antes de empacotar.
- A externalização de credenciais pertence a uma sprint de segurança separada.

## Validação recomendada

1. Gerar o executável com a especificação oficial.
2. Iniciar o executável em ambiente limpo.
3. Validar templates, fontes e modelos.
4. Validar consulta, QR Code, composição e impressão.
5. Gerar o instalador oficial e repetir o teste em máquina limpa.
