# SM64 PT-BR Xbox 360 — v0.9 NATIVE60 FINAL60 RC1

Data do checkpoint: 2026-09-17

## Estado
- PASS_STATIC_VALIDATION_HARDWARE_PENDING
- Base: v0.8 NATIVE60 RETIME CORE A, por sua vez derivada da v0.7 native60 e da v0.4 PT-BR.
- Meta: 60 Hz / 60 atualizações reais por segundo, sem duplicação de frames e sem interpolação do renderer.

## Artefatos
- XEX: `/mnt/data/SM64_PTBR_XBOX360_v0.9_NATIVE60_FINAL60_RC1.xex`
- ZIP: `/mnt/data/SM64_PTBR_XBOX360_v0.9_NATIVE60_FINAL60_RC1_PARA_TESTE.zip`
- Script de build: `/mnt/data/_sm64_native60/build_v09_final60_rc1.py`
- Report: `/mnt/data/_sm64_native60/v09_final60_rc1_report.json`
- Cave ASM: `/mnt/data/_sm64_native60/v09_cave.s`
- Cave final disassembly: `/mnt/data/_sm64_native60/v09_final_cave.disasm`

## SHA-256
- XEX: `7009c42c7962090d045d9e547037f1ff7c88f4992633903718afc41d00bfd856`
- ZIP: `a0b0b3658893243cf4682d57b65d1a6d6bea1c0467c7b346f8a8a56f2786eef8`
- mapped planejado: `9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12`
- mapped extraído do XEX final: `9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12`
- round-trip exato: `True`

## Preservação
- Mapper antes/depois: `b51af5c7f53d6cf7a058a3353f9de40dfbe514890a0822427c151026904d3e03` / `b51af5c7f53d6cf7a058a3353f9de40dfbe514890a0822427c151026904d3e03`
- Mapper preservado: `True`
- PT-BR, correção do canhão e base v0.8 preservados.

## Code cave
- Base: `0x823BC7B8`
- Tamanho: `0x2F8` (760 bytes)
- Final: `0x823BCAB0`
- `.text` VirtualSize: `0x32C7B8` -> `0x32CAB0`
- `.data` começa em `0x823C0000`, portanto o cave permanece dentro do gap.

## Retiming incluído
- `approach_f32`: incrementos globais de aproximação em ponto flutuante x0.5.
- `oTimer`: avanço a 30 Hz sobre loop/render 60 Hz.
- animações: avanço de keyframe legado a 30 Hz; render e estado espacial seguem 60 Hz.
- movimento genérico de objetos X/Z e Y: deslocamento x0.5.
- gravidade/buoyancy de objetos: incremento x0.5.
- movimento genérico velocity+gravity: deslocamentos e gravidade x0.5.
- drag de objetos: intensidade x0.5.
- sleeps de level script: decremento em paridade 30 Hz.
- Mario: framesSinceA/B, wallKickTimer, doubleJumpTimer, invincTimer, squishTimer, capTimer retimados.
- saúde do Mario: atualização temporal a 30 Hz.
- caminhada: aceleração/deceleração e yaw-approach retimados.
- slope acceleration, moving sand e horizontal wind retimados.
- Herdado da v0.8: chão/ar 4->2 substeps, principais gravidades do Mario x0.5, vento vertical x0.5, áudio corrigido para 60 Hz.

## Auditoria final
- 29 entradas de patch no report.
- Todos os branches do hook foram verificados no mapped final.
- Fixups do cave foram re-desmontados após inserção e apontam para os retornos esperados.
- Dois bugs encontrados antes do handoff foram corrigidos: preservação de `r11` no movimento vertical de objetos e preservação do registrador de ângulo no vento horizontal.
- XEX final reextraído e mapped é byte-a-byte idêntico à imagem planejada.

## Limitações conhecidas da RC1
- Ainda depende de teste em hardware; não promover a FINAL sem esse teste.
- Animação esquelética preserva duração segurando cada keyframe legado por 2 frames de vídeo; não há interpolação esquelética entre keyframes.
- Alguns `actionTimer` específicos, cutscenes, menus e transições podem ainda conter contadores locais a 60 Hz e exigir RC2.
- `gGlobalTimer` continua a 60 Hz por segurança do pipeline gráfico; apenas consumidores temporais selecionados são retimados.
- Algumas fórmulas não-lineares de slide/fricção podem precisar de ajuste fino após teste físico.
