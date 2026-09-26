# Reconstrução exata — v0.7 e v0.8 Native60

Em 25/09/2026, após recuperar o checkpoint integral de 17/09 e restaurar a
cadeia `pack.py + XexTool`, as versões v0.7 e v0.8 foram reconstruídas a partir
da v0.4 e comparadas com seus hashes históricos.

## v0.7 NATIVE60 CORE TEST

A v0.7 é exatamente a v0.4 com **4 posições de byte alteradas** no limitador:

| VA | Original | v0.7 |
|---|---|---|
| `0x821652A8` | `3D 6B 00 19` | `3D 6B 00 0D` |
| `0x821652B0` | `3D 6A 00 19` | `3D 6A 00 0D` |
| `0x821652B4` | `39 6B 6E 6A` | `39 6B B7 35` |

Essas instruções mudam o próximo deadline do time-base de **1.666.666** para
**833.333** ticks.

Resultados:
- mapped SHA-256:
  `4630aacb5011ec4726e8c852a05d09bf4acc1a9749913811d8267f00d6313312`
- XEX reconstruído SHA-256:
  `51d898f1d027aff2ee28f16ea43ce89672c73c0bf2212c7b3bda015ba3389382`
- o hash do XEX é idêntico ao histórico da v0.7.
- round-trip XEX -> mapped: byte a byte exato.

## v0.8 NATIVE60 RETIME CORE A

Partindo da v0.7 exata, foram recuperadas **13 entradas de patch**:

1. chão: 4 -> 2 substeps;
2. ar: 4 -> 2 substeps;
3. twirl gravity 4.0 -> 2.0;
4. cannon gravity 1.0 -> 0.5;
5. lava/star gravity 3.2 -> 1.6;
6. metal-water gravity 1.6 -> 0.8;
7. wing gravity 2.0 -> 1.0;
8. wing recovery 4.0 -> 2.0;
9. normal gravity 4.0 -> 2.0;
10. long-jump/slide gravity 2.0 -> 1.0;
11. vertical wind 1/8 -> 1/16;
12. áudio: 2 -> 1 blocos por quadro;
13. áudio: buffer x8 -> x4.

Resultados:
- mapped SHA-256:
  `b8eb88dfbb8fb11d418e17dec2693667586d4c0a3083708e43506bc838add6a2`
- XEX reconstruído SHA-256:
  `ff5c185bc6a78c38b80b14c6923bc6d94f2ff733c6e1c8f0a3855dc6c11583f6`
- o hash do XEX é idêntico ao histórico da v0.8.
- round-trip XEX -> mapped: byte a byte exato.
- mapper de controles preservado:
  `b51af5c7f53d6cf7a058a3353f9de40dfbe514890a0822427c151026904d3e03`.

## Scripts

- `scripts/recovered/native60/reconstruct_v07_native60.py`
- `scripts/recovered/native60/reconstruct_v08_retime_core_a.py`

Os scripts não incluem ou distribuem XEXs. Eles exigem as imagens mapeadas
corretas como entrada e recusam bases com SHA diferente.
