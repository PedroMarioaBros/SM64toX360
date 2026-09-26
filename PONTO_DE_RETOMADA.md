# PONTO_DE_RETOMADA

## Última versão produzida e recuperada

**SM64_PTBR_XBOX360_v0.10_NATIVE60_RC2**.

O XEX e o ZIP originais foram recuperados em bytes — a limitação forense anterior
foi superada.

- XEX: 14.983.168 bytes  
  SHA-256 `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7`
- ZIP: 14.990.594 bytes  
  SHA-256 `c3d67872da96a3f3646a6f62a10fadd0b9195220bf20e8817f913486ca5a3455`
- mapped:  
  SHA-256 `b87b33f3664aaefe3d7163d998f0535a666f13437b9f4d91f556bad49512426b`

O ZIP original também preservou `v010_rc2_report.json` e
`V010_NATIVE60_RC2_PROGRESS.md`.

## Reconstrução independente

A RC2 foi reconstruída a partir da v0.9 recuperada, usando somente os patches
documentados e a extensão PPC real de 348 bytes. O XEX produzido ficou
**byte a byte idêntico** ao XEX original acima. O round-trip XEX → mapped também
foi exato.

A v0.9, v0.8 e v0.7 também foram reconstruídas com a mesma identidade byte a byte.

## Última versão com feedback de hardware localizado

**v0.9 NATIVE60 FINAL60 RC1**.

Problemas registrados no Xbox:
- moedas e outros estados visuais acelerados;
- Mario da abertura e APERTE START acelerados;
- bolas/Bob-ombs acelerados;
- casco Koopa quase parado/lento;
- sobreposição/tremulação ocasional do Mario ao andar/virar rápido.

## O que a v0.10 corrigiu no binário

O report original comprova:
- correção do erro `update_shell_speed` vs `update_walking_speed`;
- retiming real da caminhada;
- retiming de `object_step`;
- moedas;
- Bob-ombs;
- abertura/Goddard;
- logo/TM;
- APERTE START;
- idle demo.

A RC2 **não afirma** resolver o ghosting/sobreposição ocasional; isso ficou como
item de observação.

## Próximo teste de hardware

Testar a v0.10 original/reconstruída e verificar:

1. boot, menu e save existente;
2. caminhada/corrida/saltos em velocidade normal;
3. moedas;
4. APERTE START;
5. abertura/logo/demo;
6. Bob-ombs e bolas da montanha;
7. casco Koopa;
8. áudio e timers;
9. câmera/giro rápido e possível ghosting;
10. cannon fix, saves, PT-BR e menus sem regressão.

## Direção depois desse teste

A base padrão do projeto continua em **30 FPS**. A cadeia Native60 recuperada é
a referência técnica para a futura opção 60 FPS do **Modo Xbox 360**.

O próximo desenvolvimento maior (Modo Xbox/câmera moderna) só deve avançar sobre
uma base validada no console, para não misturar bugs de timing com mudanças de
jogabilidade.
