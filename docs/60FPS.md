# 60 FPS — histórico e estado técnico

## Direção canônica atual

O jogo base permanece em **30 FPS**, fiel ao original, com PT-BR e controles
Xbox 360. O modo 60 FPS passa a ser uma opção do futuro **Modo Xbox 360**
(Back/Select), e não uma alteração obrigatória da base.

## Linha experimental — bytes recuperados

Toda a sequência v0.5→v0.10 está agora recuperada em bytes:

- **v0.5 — DIAG 60HZ DUPLICADO**  
  Segundo quadro visual adicional a ~60 apresentações, lógica ~30 Hz, sem interpolação.
- **v0.6 — INTERPOLADO Y 30/60**  
  Interpolação de matrizes no renderer, seletor Y 30/60 e overlay temporário.
  Essa arquitetura foi posteriormente abandonada.
- **v0.7 — NATIVE60 CORE TEST**  
  Loop inteiro ~60 Hz, sem duplicação e sem interpolação. Hardware confirmou
  fluidez, mas sistemas frame-dependent ficaram ~2x.
- **v0.8 — NATIVE60 RETIME CORE A**  
  Retiming inicial de substeps, gravidades, vento vertical e áudio.
- **v0.9 — NATIVE60 FINAL60 RC1**  
  Retiming amplo via cave de 760 bytes e 27 hooks.
- **v0.10 — NATIVE60 RC2**  
  Corrige o erro shell/walking da RC1 e amplia retiming de object_step,
  moedas, Bob-ombs, abertura/logo e APERTE START.

## Reconstrução exata

As versões v0.7, v0.8, v0.9 e v0.10 foram reconstruídas a partir das bases
anteriores e seus XEXs resultaram **byte a byte idênticos** aos originais
recuperados.

| Versão | mapped SHA-256 | XEX SHA-256 |
|---|---|---|
| v0.7 | `4630aacb5011ec4726e8c852a05d09bf4acc1a9749913811d8267f00d6313312` | `51d898f1d027aff2ee28f16ea43ce89672c73c0bf2212c7b3bda015ba3389382` |
| v0.8 | `b8eb88dfbb8fb11d418e17dec2693667586d4c0a3083708e43506bc838add6a2` | `ff5c185bc6a78c38b80b14c6923bc6d94f2ff733c6e1c8f0a3855dc6c11583f6` |
| v0.9 | `9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12` | `7009c42c7962090d045d9e547037f1ff7c88f4992633903718afc41d00bfd856` |
| v0.10 | `b87b33f3664aaefe3d7163d998f0535a666f13437b9f4d91f556bad49512426b` | `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7` |

## v0.9 RC1

- cave: `0x823BC7B8..0x823BCAB0` — 760 bytes;
- `.text`: `0x32C7B8 -> 0x32CAB0`;
- 27 hooks diretos + cave + VirtualSize = 29 entradas de patch;
- retiming de oTimer, animação, objetos genéricos, sleeps, timers do Mario,
  saúde, slope, moving sand e horizontal wind.

O feedback em hardware da RC1 apontou: moedas, abertura/Mario, APERTE START,
Bob-ombs/bolas ainda acelerados; casco Koopa excessivamente lento; e
sobreposição/tremulação ocasional do Mario em mudança rápida de direção.

## v0.10 RC2

A RC2 comprovadamente:

- restaura os patches indevidos de `update_shell_speed`;
- aplica aceleração/deceleração/yaw à função real de caminhada;
- retima `object_step` (XZ, Y, gravidade, fricção e damping);
- retima moedas e Bob-ombs;
- corrige abertura/Goddard, logo/TM, APERTE START e idle demo;
- adiciona 348 bytes de cave em `0x823BCAB0..0x823BCC0C`;
- amplia `.text` para `0x32CC0C`.

O mapped e o XEX originais foram recuperados e os hashes históricos foram
recomputados integralmente. **Ainda falta o teste de hardware da RC2.**

## Scripts públicos de reconstrução

- `reconstruct_v07_native60.py`
- `reconstruct_v08_retime_core_a.py`
- `reconstruct_v09_final60_rc1.py`
- `reconstruct_v10_native60_rc2.py`

Eles armazenam somente os patches/código PPC próprio e exigem a base correta por SHA.
