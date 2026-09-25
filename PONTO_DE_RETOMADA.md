# PONTO_DE_RETOMADA

## Última versão comprovadamente produzida

**SM64_PTBR_XBOX360_v0.10_NATIVE60_RC2**. Existem entradas reais na Biblioteca para o XEX (14.983.168 bytes) e o ZIP de teste (14.990.594 bytes), criadas em 19/09/2026. O histórico registra SHA-256 do XEX `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7` e do ZIP `c3d67872da96a3f3646a6f62a10fadd0b9195220bf20e8817f913486ca5a3455`.

**Limitação forense:** na auditoria os bytes raw desses dois Project files não puderam ser materializados. Os hashes são históricos, não recomputados.

## Última versão comprovadamente testada

**v0.9 NATIVE60 FINAL60 RC1**. O histórico contém feedback de teste no Xbox 360: moedas, animação inicial do Mario e `APERTE START` ainda acelerados; sobreposição/tremulação ao andar/virar rápido; bolas/Bob-ombs acelerados; casco Koopa quase parado/lento embora o salto estivesse rápido.

## Versão seguinte produzida e ainda aguardando teste

**v0.10 NATIVE60 RC2**. Não foi localizado feedback posterior de execução dessa versão no console.

## O que ela pretendia corrigir

Segundo o registro de entrega, a RC2 corrigia a identificação errada entre `update_shell_speed()` e `update_walking_speed()` e adicionava/ajustava retiming para casco, caminhada, Bob-ombs, bolas da montanha, moedas, abertura/Mario/logo, `APERTE START`, demo e timers. A questão de overlay visual em movimentos rápidos não estava comprovadamente resolvida.

## Arquivos correspondentes

- `SM64_PTBR_XBOX360_v0.10_NATIVE60_RC2.xex`
- `SM64_PTBR_XBOX360_v0.10_NATIVE60_RC2_PARA_TESTE.zip`

Eles foram localizados na Biblioteca, mas não recuperados em bytes para o pacote de migração. Não existe placeholder nem XEX recriado com esses nomes.

## O que testar no Xbox 360 quando o arquivo original voltar a ficar acessível

1. boot, menu e carregamento de save existente;
2. velocidade normal de Mario andando/correndo/pulando;
3. moedas e `APERTE START` em cadência normal;
4. abertura/logo/demo;
5. Bob-ombs e bolas da montanha;
6. casco Koopa como “skate”, sem lentidão extrema;
7. áudio e timers;
8. câmera em giro rápido e possível overlay/ghosting;
9. canhão, saves e correções PT-BR/menu sem regressão;
10. estabilidade prolongada em hardware real.

## Próximo passo

Se RC2 corrigir a cadência sem regressões, registrar resultados e congelar a engenharia 60 FPS como referência para a opção futura do **Modo Xbox 360**. Se falhar, comparar especificamente com RC1 e corrigir somente subsistemas reproduzidos no teste. Em ambos os casos, a direção atual mantém **30 FPS como base padrão**; 60 FPS passa a ser opção do Modo Xbox 360.