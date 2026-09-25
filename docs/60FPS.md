# 60 FPS — histórico e estado técnico

## Direção canônica atual

A decisão atual do projeto é preservar o jogo base em **30 FPS**, fiel ao original,
com PT-BR e controles Xbox 360. O modo 60 FPS deve ser uma opção dentro do futuro
menu **Modo Xbox 360** (Back/Select), e não uma alteração obrigatória da base.

## Linha experimental recuperada

A Biblioteca registra builds reais v0.5 a v0.10, cada uma com XEX e pacote de
teste. Os byte streams desses builds ainda não foram materializados nesta retomada,
portanto eles não são recriados nem publicados como placeholders.

- v0.5 — DIAG 60HZ DUPLICADO
- v0.6 — INTERPOLADO Y 30/60
- v0.7 — NATIVE60 CORE TEST
- v0.8 — NATIVE60 RETIME CORE A
- v0.9 — NATIVE60 FINAL60 RC1
- v0.10 — NATIVE60 RC2

## v0.7 — prova de 60 Hz em hardware

O checkpoint `V08_RETIMER_PROGRESS.md` registra que a v0.7 foi executada no
Xbox 360 com jogo inteiro, menus e áudio aproximadamente 2x mais rápidos, mas
muito fluida e sem ghosting/interpolação. A conclusão técnica daquele teste foi
que o port/hardware sustentava o loop completo em ~60 Hz; o problema remanescente
era retimar os sistemas dependentes de quadro.

## v0.9 NATIVE60 FINAL60 RC1 — engenharia recuperada em texto

O arquivo real `V09_FINAL60_RC1_PROGRESS.md` foi recuperado em texto. Ele registra:

- XEX histórico: `7009c42c7962090d045d9e547037f1ff7c88f4992633903718afc41d00bfd856`
- ZIP histórico: `a0b0b3658893243cf4682d57b65d1a6d6bea1c0467c7b346f8a8a56f2786eef8`
- mapped planejado/final: `9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12`
- round-trip registrado: exato
- code cave: `0x823BC7B8` → `0x823BCAB0`
- tamanho do cave: `0x2F8` (760 bytes)
- `.text` VirtualSize: `0x32C7B8` → `0x32CAB0`
- 29 entradas de patch no report histórico

Retiming registrado na RC1: `approach_f32`, `oTimer`, animações, movimento
genérico de objetos X/Z/Y, gravidade/buoyancy, velocity+gravity, drag, sleeps de
level script, timers do Mario, saúde, caminhada, slope acceleration, moving sand,
horizontal wind e correções herdadas da v0.8 para substeps, gravidades e áudio.

O mesmo checkpoint registra dois bugs corrigidos antes do handoff: preservação de
`r11` no movimento vertical de objetos e preservação do registrador de ângulo no
vento horizontal.

## Último teste de hardware localizado

A **v0.9 NATIVE60 FINAL60 RC1** é a última versão para a qual foi localizado
feedback explícito posterior de execução no Xbox 360. Ainda foram relatados
problemas de cadência/velocidade em moedas, abertura/Mario, `APERTE START`,
Bob-ombs, bolas e casco Koopa, além de sobreposição/tremulação em movimento rápido.

## v0.10 NATIVE60 RC2 — última build produzida

A **v0.10 NATIVE60 RC2** é a última build cuja existência foi comprovada na
Biblioteca. O histórico registra correção da confusão entre
`update_shell_speed()` e `update_walking_speed()` e ampliação do retiming para
casco, Bob-ombs, bolas, moedas, abertura/logo, `APERTE START`, demo/timers e
`object_step()`.

Hashes históricos:
- XEX v0.10: `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7`
- mapped v0.10: `b87b33f3...2426b` (registro histórico abreviado; não recomputado)
- ZIP v0.10: `c3d67872da96a3f3646a6f62a10fadd0b9195220bf20e8817f913486ca5a3455`

O byte stream da v0.10 continua inacessível nesta retomada e não foi localizado
teste posterior dela no console. Nenhum arquivo substituto foi inventado.
