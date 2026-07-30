# Estrutura do projeto

## Fontes oficiais

| Caminho | Papel |
|---|---|
| `app/` | Código principal da aplicação |
| `app/ui/` | Interface gráfica ativa |
| `app/vision/` | Integração ativa de visão/SisWeb |
| `config/` | Configuração de execução e integrações |
| `templates/` | Templates dos crachás |
| `fonts/` | Fontes da composição |
| `models/` | Modelos de visão computacional |
| `installer/` | Fonte oficial do instalador |
| `SistemaCrachaCDN.spec` | Especificação oficial do PyInstaller |
| scripts `.bat` da raiz | Automação oficial de build e instalador |
| `docs/` | Documentação mantida do projeto |

## Artefatos locais

`build/`, `dist/`, `dist_instalador/`, `output/`, `logs/`, `fotos_temp/`, caches e ambientes virtuais são saídas ou dados locais, não fontes do produto.

## Legado e duplicações avaliadas

| Caminho | Classificação | Evidência | Recomendação futura |
|---|---|---|---|
| `app/ui_backup_v2/` | Backup legado | Snapshot de UI não importado pelo runtime | Arquivar após teste de regressão |
| `app/ui_backup_v5/` | Backup legado | Snapshot mais recente, mas diferente da UI oficial | Comparar diferenças úteis e arquivar |
| `Gerador_EXE_SistemaCracha_CDN/` | Pacote legado de build | Duplica spec, scripts e recursos | Arquivar após validar o fluxo oficial da raiz |
| `SistemaCracha_Instalador_Arquivos/` | Pacote legado/incompleto | Duplica instalador e scripts; isoladamente referencia arquivo ausente | Arquivar após validar `installer/` |
| `Modulo_SisWeb_Integracao/` | Pacote legado de integração | Duplica módulos de `app/vision/` e não é importado pelo runtime | Arquivar após teste funcional do SisWeb oficial |

## Decisão da Sprint 1

Nenhuma das pastas acima foi removida. Elas permanecem para preservar rastreabilidade até que testes de caracterização e validação operacional autorizem o arquivamento.

## Documentação histórica

Os arquivos anteriores foram preservados em `docs/legacy/`, separados por origem. Eles servem como referência histórica e não substituem os documentos atuais.
