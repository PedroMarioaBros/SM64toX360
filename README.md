# SM64toX360 — migração canônica do projeto

Este repositório é a fonte canônica do projeto **Super Mario 64 para Xbox 360 / SM64toX360**.

A auditoria de 25/09/2026 separou rigorosamente quatro classes de evidência:

1. **RAW_RECUPERADO** — bytes reais materializados e hash SHA-256 recomputado.
2. **TEXTO_INDEXADO** — conteúdo textual ainda legível no armazenamento, mas sem acesso ao byte stream original na auditoria.
3. **METADADO_SEM_RAW** — entrada real existente na Biblioteca, com nome/tamanho/data, porém sem bytes recuperados.
4. **HISTÓRICO_SEM_ARQUIVO** — fato/arquivo mencionado nos chats, sem artefato correspondente localizado.

> O pacote integral de migração contém uma área `RECUPERADOS_NAO_PUBLICAR/` com XEXs, ZIPs, imagens e material derivado do jogo original. Esse conteúdo foi preservado para continuidade técnica e análise de direitos e não é publicado automaticamente neste repositório.

## Estado técnico resumido

- Base corrigida preservada: `sm64corrigido.xex`, SHA-256 `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`.
- Versão PT-BR funcional de referência: **0.4**, XEX SHA-256 `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`.
- Última versão 60 FPS **com teste de hardware comprovado**: **v0.9 NATIVE60 FINAL60 RC1**.
- Última versão 60 FPS **produzida**: **v0.10 NATIVE60 RC2**; não foi localizado registro posterior de teste no console.
- Direção atual: jogo base fiel a **30 FPS**; melhorias extras, inclusive 60 FPS, ficam no menu **Modo Xbox 360** por Back/Select.

Leia primeiro `PONTO_DE_RETOMADA.md`.