# Status atual

## Base recuperada e reconstruível

- `sm64corrigido.xex`: SHA-256
  `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`.
- PT-BR v0.4: SHA-256
  `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`.
- checkpoint completo de 17/09: **80.704.194 bytes**, 56/56 hashes internos válidos.
- pipeline `pack.py + XexTool` restaurado: a v0.4 foi reconstruída com XEX
  **bit a bit idêntico** ao original.

## Linha Native60 totalmente recuperada

Os XEXs e ZIPs originais de **v0.5, v0.6, v0.7, v0.8, v0.9 e v0.10** foram
materializados em bytes. A limitação anterior de “metadado sem raw” deixou de
existir para essa linha.

Também foram recuperados dos ZIPs os relatórios/checkpoints técnicos originais.

### Reconstruções exatas comprovadas

- v0.7 → XEX `51d898f1d027aff2ee28f16ea43ce89672c73c0bf2212c7b3bda015ba3389382`
- v0.8 → XEX `ff5c185bc6a78c38b80b14c6923bc6d94f2ff733c6e1c8f0a3855dc6c11583f6`
- v0.9 → XEX `7009c42c7962090d045d9e547037f1ff7c88f4992633903718afc41d00bfd856`
- v0.10 → XEX `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7`

Cada um desses XEXs reconstruídos ficou **byte a byte idêntico** ao original
recuperado. O round-trip XEX → mapped também foi exato.

## Estado de teste em hardware

- 0.3: save/load e “Salvar e sair” confirmados no histórico.
- 0.4: funcionalidade no Xbox registrada.
- v0.5: o pacote recuperado registra teste bem-sucedido em hardware.
- v0.7: hardware confirmou loop ~60 Hz extremamente fluido, porém lógica/menu/áudio ~2x.
- v0.9: último feedback de hardware localizado; ainda havia subsistemas acelerados,
  casco lento e sobreposição/tremulação ocasional.
- v0.10: bytes originais recuperados e engenharia comprovada, mas **não foi
  localizado teste posterior da RC2 no console**.

## Toolchain aberta para Xbox 360

O run #20 de `PedroMarioaBros/OpenXeChain-X360-Builder` comprovou build completo
do OpenXeChain e geração de um `hello.xex` com magic `XEX2`.

- `hello.xex`: `b5a74eb8781411d03ec7ee16d4c54736a68b890f0dd0bf4545121d097faaf7a5`
- toolchain: `c71a1a4586a2eb1741c632b164ad74e90532cdb7bf0851774544998b35312d37`

A toolchain foi preservada em Release permanente. O XexTool oficial Linux também
foi recuperado/verificado e o repack da família SM64 voltou a funcionar localmente.

## Próximas etapas

1. Testar a **v0.10 RC2 original** em Xbox 360 real, comparando especificamente
   os problemas observados na RC1.
2. Registrar esse resultado como novo checkpoint de hardware.
3. Preservar **30 FPS como base canônica** e usar a engenharia Native60 como
   referência da futura opção 60 FPS do **Modo Xbox 360**.
4. Continuar o Modo Xbox 360/câmera moderna somente sobre uma base de hardware
   estável, sem perder PT-BR, saves, cannon fix ou controles.
