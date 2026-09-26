# Reconstrução exata — v0.9 RC1 e v0.10 RC2

Em 25/09/2026, os byte streams originais das builds v0.9 e v0.10 foram
recuperados da Biblioteca e comparados com reconstruções determinísticas.

## v0.9 NATIVE60 FINAL60 RC1

Base obrigatória: mapped v0.8
`b8eb88dfbb8fb11d418e17dec2693667586d4c0a3083708e43506bc838add6a2`.

A RC1 aplica 27 hooks/patches diretos, injeta uma cave PPC de **760 bytes** em
`0x823BC7B8..0x823BCAB0` e amplia `.text` de `0x32C7B8` para
`0x32CAB0`.

Resultado reconstruído:
- mapped SHA-256: `9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12`;
- XEX SHA-256: `7009c42c7962090d045d9e547037f1ff7c88f4992633903718afc41d00bfd856`;
- XEX reconstruído **byte a byte idêntico** ao original recuperado;
- round-trip XEX -> mapped exato.

A RC1 retima oTimer, animações, integração genérica de objetos, sleeps, vários
timers do Mario, saúde, slope acceleration, moving sand e horizontal wind.
Posteriormente foi comprovado que três patches rotulados como caminhada atingiam
`update_shell_speed`; a RC2 corrige esse mapeamento.

## v0.10 NATIVE60 RC2

Base obrigatória: mapped v0.9
`9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12`.

A RC2 restaura os patches indevidos do casco, move o retiming para a função real
de caminhada, acrescenta retiming de `object_step`, moedas, Bob-ombs, abertura,
logo/TM e `APERTE START`. A extensão PPC tem **348 bytes**, em
`0x823BCAB0..0x823BCC0C`, e `.text` passa para `0x32CC0C`.

Resultado reconstruído:
- mapped SHA-256: `b87b33f3664aaefe3d7163d998f0535a666f13437b9f4d91f556bad49512426b`;
- XEX SHA-256: `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7`;
- XEX reconstruído **byte a byte idêntico** ao original recuperado;
- round-trip XEX -> mapped exato;
- mapper de controles preservado.

## Scripts

- `scripts/recovered/native60/reconstruct_v09_final60_rc1.py`
- `scripts/recovered/native60/reconstruct_v10_native60_rc2.py`

Os scripts contêm apenas patches e código PPC injetado do nosso trabalho. Eles
não contêm o executável do jogo e recusam bases com SHA incorreto.
