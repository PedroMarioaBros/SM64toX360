# Manifesto da migração

Auditoria realizada em 25/09/2026. O pacote de migração foi validado com SHA-256 `e3227b93677d1103bff57ede41060e87bbdd6de03cc03d39ff57a26ebc162c84`.

## Classes de evidência

- **RAW_RECUPERADO**: bytes reais recuperados e hash recomputado.
- **METADADO_SEM_RAW**: arquivo real localizado na Biblioteca, mas sem byte stream materializável durante a auditoria.
- **TEXTO_INDEXADO**: conteúdo textual recuperável, mas não necessariamente o arquivo original byte a byte.
- **HISTÓRICO_SEM_ARQUIVO**: menção comprovada no histórico sem artefato recuperado.

## Principais arquivos RAW recuperados

- `sm64corrigido.xex` — base corrigida — SHA-256 `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`.
- `sm64-ptbr-teste.xex` — PT-BR 0.4 — SHA-256 `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`.
- `SUPER MARIO 64 360 EDITION.zip` — base — SHA-256 `d146a3f57d7023648bbdbba7f2644296c793629dba4301fc12e157af7900297a`.
- pacote PT-BR 0.3 — SHA-256 `7123e27c52aa862e51e403a1bba52b94a7dc055eccc33f413bd31f253dad3dcf`.
- pacote PT-BR 0.4 — SHA-256 `d31bdd7d8396bbeeea2805dd9cdb3f7bfbfee106bf1fc2380b19bc76e33e2b78`.
- checkpoint completo de 17/09/2026 — SHA-256 `265a6cdfba9e4dfaded578462a1388d4b97a1246643fd72d5ed8cdd4913e6368`.

Esses binários/pacotes foram preservados na camada de revisão, mas não publicados automaticamente neste repositório público.

## Builds 60 FPS localizadas por metadado

Existem entradas reais para v0.5, v0.6, v0.7, v0.8, v0.9 e v0.10 (XEX + ZIP). Seus bytes não puderam ser materializados durante a auditoria. Não foram recriados placeholders.

A última versão com teste de hardware localizado é v0.9 RC1. A última versão produzida é v0.10 RC2, ainda sem teste posterior localizado.

## Material de outro projeto

Foram encontrados vários pacotes `SMB360_XEX_TESTE_*`. Eles pertencem à cadeia experimental do Super Mario Bros. NES e **não são versões do SM64**. Não foram migrados para este repositório.

## Política

Nenhum XEX, ROM, ZIP com binário/arte proprietária, dump ou imagem mapeada é publicado automaticamente. O repositório público contém documentação própria e registros técnicos apropriados para continuidade do projeto.