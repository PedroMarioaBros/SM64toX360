# SM64toX360 — migração canônica do projeto

Este repositório é a fonte canônica do projeto **Super Mario 64 para Xbox 360 / SM64toX360**.

A auditoria de 25/09/2026 separa rigorosamente quatro classes de evidência:

1. **RAW_RECUPERADO** — bytes reais materializados e SHA-256 recomputado.
2. **TEXTO_INDEXADO** — conteúdo textual ainda legível, sem necessariamente preservar o arquivo original byte a byte.
3. **METADADO_SEM_RAW** — entrada real localizada, mas sem byte stream recuperado.
4. **HISTÓRICO_SEM_ARQUIVO** — menção no histórico sem artefato correspondente localizado.

> XEXs, ZIPs contendo o jogo, imagens mapeadas e outros materiais binários/derivados
> são preservados fora deste repositório público. O GitHub contém documentação,
> scripts próprios e registros técnicos necessários para reconstrução.

## Estado técnico resumido

- Base corrigida preservada: `sm64corrigido.xex` — SHA-256
  `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`.
- PT-BR funcional de referência: **v0.4** — SHA-256
  `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`.
- Checkpoint completo de 17/09 recuperado: **80.704.194 bytes**, 56/56 hashes internos válidos.
- Toda a linha experimental **v0.5 a v0.10** foi recuperada em bytes (XEX + ZIP).
- As versões **v0.7, v0.8, v0.9 e v0.10** foram também reconstruídas
  deterministicamente e deram XEX **byte a byte idêntico** aos originais.
- Última versão 60 FPS com feedback de hardware localizado: **v0.9 FINAL60 RC1**.
- Última versão produzida: **v0.10 NATIVE60 RC2**; o XEX original foi recuperado,
  mas ainda não foi localizado teste posterior dessa RC2 no console.
- Toolchain OpenXeChain comprovada até XEX2 e XexTool multiplataforma restaurado.
- Direção atual do produto: jogo base fiel a **30 FPS**; 60 FPS e demais extras
  ficam como futuras opções do **Modo Xbox 360** por Back/Select.

Leia primeiro `PONTO_DE_RETOMADA.md`.
