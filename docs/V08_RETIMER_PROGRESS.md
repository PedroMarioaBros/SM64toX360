# CHECKPOINT — v0.8 NATIVE60 RETIMER
Data: 2026-09-17

## Hardware test confirmado
v0.7 NATIVE60 CORE: jogo inteiro, menus e audio ~2x, mas extremamente fluido e sem ghosting/interpolacao.
Conclusao: Xbox 360/port sustentam loop completo em ~60 Hz; problema agora e exclusivamente retiming de sistemas frame-dependent.

## Base obrigatoria
- Partir de v0.4 PT-BR limpa ou da v0.7 (v0.4 + timer 60 Hz).
- Nao usar codigo/interpolacao da v0.5/v0.6.
- Nao alterar mapper 0x82165998-0x82165C90.
- Preservar PT-BR, bug do canhao, menus e controles.

## Binario
- mapped base: 0x82000000
- game_loop_one_iteration: 0x8203D0B8
- audio_game_loop_tick: ~0x820A3958
- select_gfx_pool: 0x8203C958
- read_controller_inputs: 0x8203CCF8
- level_script_execute: 0x82005448
- display_and_vsync: 0x8203C9C8
- timer backend: 0x82165230
- produce_one_frame: 0x8215CF18
- 60 Hz interval: 833333 ticks

## Pesquisa externa descartada como solucao direta
- CalebVernon/SM64-60-Project: 30 Hz logic + frame lerp/alternancia.
- rovertronic/HackerSM64-60threaded: renderer thread + lerp/double buffering.
- Kaze 60 FPS v2: inclui paridade/cache/interpolacao; util como mapa, nao como arquitetura alvo.
- Historico Giorgis20 commit 733fafc0 ('Fix the build'): sem backend XDK/XEX/XAM/Direct3D recuperavel.

## Proxima etapa
Mapear no PPC funcoes centrais de:
1. Mario/physics integration
2. generic object movement + oTimer
3. animation frame advancement
4. camera approach/smoothing
5. menu/global timers
6. audio cadence
Depois construir v0.8 RETIME CORE por subsistemas, sem renderer interpolation.

## Correcao critica de enderecamento
`text.raw`/`text.elf` representa somente a secao `.text`, cuja VA inicial e 0x82090000.
Portanto enderecos derivados de offset do text precisam de +0x82090000.
Exemplos corrigidos:
- game_loop_one_iteration: 0x820CD0B8
- audio_game_loop_tick: 0x82133958
- select_gfx_pool: 0x820CC958
- read_controller_inputs: 0x820CCCF8
- level_script_execute: 0x82095448
- display_and_vsync: 0x820CC9C8
Os enderecos conhecidos produce_one_frame 0x8215CF18 e timer 0x82165230 ja estavam em VA correta.
