# 60 FPS — histórico e estado técnico

## Direção canônica atual

A decisão atual do projeto é preservar o jogo base em **30 FPS**, fiel ao original, com PT-BR e controles Xbox 360. O modo 60 FPS deve ser uma opção dentro do futuro menu **Modo Xbox 360** (Back/Select), e não uma alteração obrigatória da base.

## Linha experimental recuperada

A Biblioteca registra builds reais v0.5 a v0.10, cada uma com XEX e pacote de teste. Na auditoria de migração, os metadados estavam acessíveis, mas os bytes raw dessas entradas não puderam ser materializados. Portanto, não são recriados nem publicados como placeholders.

- v0.5 — DIAG 60HZ DUPLICADO
- v0.6 — INTERPOLADO Y 30/60
- v0.7 — NATIVE60 CORE TEST
- v0.8 — NATIVE60 RETIME CORE A
- v0.9 — NATIVE60 FINAL60 RC1
- v0.10 — NATIVE60 RC2

## Último teste de hardware localizado

A **v0.9 NATIVE60 FINAL60 RC1** é a última versão para a qual foi localizado feedback explícito de execução no Xbox 360. Permaneciam problemas de cadência/velocidade em moedas, abertura/Mario, APERTE START, Bob-ombs, bolas e casco Koopa, além de relato de sobreposição/tremulação em movimento rápido.

## Última build produzida

A **v0.10 NATIVE60 RC2** é a última build cuja existência foi comprovada na Biblioteca. O histórico registra que ela pretendia corrigir a identificação entre rotinas de casco/caminhada e ampliar o retiming de vários subsistemas. Não foi localizado feedback posterior de teste dessa RC2 no console.

Hashes históricos:
- XEX v0.10: `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7`
- ZIP v0.10: `c3d67872da96a3f3646a6f62a10fadd0b9195220bf20e8817f913486ca5a3455`

Esses hashes não foram recomputados nesta migração porque o byte stream da v0.10 não estava disponível.