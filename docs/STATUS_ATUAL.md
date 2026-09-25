# Status atual

## Comprovado por bytes recuperados

- `sm64corrigido.xex`: base corrigida, SHA-256 `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`.
- `sm64-ptbr-teste.xex`: versão 0.4, SHA-256 `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`.
- pacote 0.3 e pacote 0.4.
- checkpoint completo de 17/09/2026.
- quatro fotos dos menus usadas no diagnóstico visual.

### Checkpoint de 17/09 recuperado novamente

Na continuação da auditoria em 25/09/2026, o arquivo real
`SM64_PTBR_XBOX360_CHECKPOINT_COMPLETO_2026-09-17.zip` foi novamente materializado
em bytes.

- tamanho: **80.704.194 bytes**
- SHA-256 recomputado: `265a6cdfba9e4dfaded578462a1388d4b97a1246643fd72d5ed8cdd4913e6368`
- manifesto interno: **56/56 arquivos verificados por SHA-256**

O checkpoint contém, entre outros itens, os XEX de referência 0.4/base corrigida,
imagens mapeadas, `text.raw`, `text.elf`, disassemblies, scripts reais de
extração/build/repack/verificação e o projeto técnico da 0.4. Esses materiais
permanecem fora do repositório público quando incluem binário ou conteúdo derivado
do jogo.

## Linha 60 FPS

As v0.5, v0.6, v0.7, v0.8, v0.9 e v0.10 possuem entradas XEX e ZIP reais na
Biblioteca. Os byte streams desses XEX/ZIP específicos continuam indisponíveis para
materialização nesta retomada.

O documento real `V09_FINAL60_RC1_PROGRESS.md` foi recuperado em texto e registra
a engenharia da v0.9, inclusive hashes, code cave e retiming. Isso não equivale a
ter recuperado o XEX v0.9.

## Estado de teste

- 0.3: teste de save/load e “Salvar e sair” confirmado no histórico e citado no LEIA-ME da 0.4.
- 0.4: documentação posterior registra relato do usuário de que funcionou no Xbox.
- v0.7: teste de hardware registrou loop completo ~60 Hz, porém jogo/menu/áudio ~2x.
- v0.9: última versão 60 FPS com feedback de hardware encontrado.
- v0.10: última versão produzida; teste posterior não encontrado.

## Toolchain aberta para Xbox 360

O repositório auxiliar `PedroMarioaBros/OpenXeChain-X360-Builder` já comprovou
em GitHub Actions a compilação completa do OpenXeChain (Clang/LLVM, xecorelib,
Newlib, compiler-rt e SynthXEX). A validação final de geração de um XEX smoke
`XEX2` está sendo executada nos runs #20/#21.

## Pendências imediatas

1. Concluir a prova de geração XEX2 da toolchain OpenXeChain.
2. Preservar a base canônica em 30 FPS e tratar 60 FPS como opção futura do **Modo Xbox 360**.
3. Recuperar/testar a v0.10 RC2 caso o byte stream original volte a ficar acessível.
4. Não publicar XEXs/ZIPs/dumps/imagens mapeadas no GitHub público sem revisão de direitos.
