# Recuperação verificada — checkpoint de 17/09/2026

## Arquivo

`SM64_PTBR_XBOX360_CHECKPOINT_COMPLETO_2026-09-17.zip`

- tamanho materializado: **80.704.194 bytes**
- SHA-256 recomputado: `265a6cdfba9e4dfaded578462a1388d4b97a1246643fd72d5ed8cdd4913e6368`
- manifesto interno: **56 linhas / 56 arquivos**
- validação: **56/56 hashes conferidos**

A recuperação ocorreu novamente durante a retomada de 25/09/2026. Isso elimina a
incerteza anterior sobre o byte stream do checkpoint: o ZIP existe e foi lido em
sua forma original.

## Conteúdo técnico confirmado

O arquivo contém:

- `binarios/sm64corrigido.xex`
- `binarios/sm64-ptbr-0.4.xex`
- `engenharia_reversa/sm64corrigido.mapped.bin`
- `engenharia_reversa/sm64-ptbr-0.4.mapped.bin`
- `engenharia_reversa/text.raw`
- `engenharia_reversa/text.elf`
- `engenharia_reversa/entry.disasm`
- `engenharia_reversa/pcmain_region.disasm`
- scripts de extração e busca de referências
- pipeline completo da revisão PT-BR 0.4
- documentação de controles e pendências visuais

## Hashes centrais conferidos pelo manifesto

- base corrigida XEX: `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`
- PT-BR 0.4 XEX: `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`
- mapped base corrigida: `75f653c7383b8cbbd218449bbd7ea45c787b7bf62db3d9e312356517834a91c7`
- mapped PT-BR 0.4: `6381bf1333bf1985474af00c139f33f9cdbad71a371c3231db0d861b72cfac2c`
- pacote original: `d146a3f57d7023648bbdbba7f2644296c793629dba4301fc12e157af7900297a`
- pacote PT-BR 0.4: `d31bdd7d8396bbeeea2805dd9cdb3f7bfbfee106bf1fc2380b19bc76e33e2b78`

## Limite desta recuperação

O checkpoint é anterior à linha final v0.8/v0.9/v0.10. Ele prova e preserva a base
0.4 e a engenharia inicial do 60 FPS, mas não contém os scripts de build
`build_v09_final60_rc1.py`, `v09_cave.s` ou os bytes da v0.10.

Por isso, a continuidade deve distinguir:

1. base/pipeline 0.4 — **RAW recuperado**;
2. progresso v0.9 — **documento técnico recuperado em texto**, XEX ainda sem raw;
3. v0.10 — **metadado + histórico**, XEX/ZIP ainda sem raw.
