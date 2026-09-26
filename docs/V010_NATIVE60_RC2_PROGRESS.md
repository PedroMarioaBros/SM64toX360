# SM64 PT-BR Xbox 360 — v0.10 NATIVE60 RC2

Base: v0.9 FINAL60 RC1.

## Motivo da RC2
Feedback de hardware da RC1: moedas, Mario da abertura, pisca de APERTE START, bolas da montanha e Bob-ombs ainda acelerados; casco Koopa excessivamente lento; sobreposição ocasional do Mario ao mudar rápido de direção.

## Correções principais
- Corrigido erro de mapeamento da RC1: 0x820ED0D8 é update_shell_speed, não update_walking_speed. Os patches indevidos do casco foram restaurados.
- update_walking_speed real em 0x820ED398 agora recebe retiming de aceleração/deceleração e yaw.
- object_step em 0x82103A08 foi retimado: deslocamento X/Z, gravidade, deslocamento Y e componentes de gravidade em piso.
- Fricção multiplicativa do object_step usa equivalente temporal de 60 Hz (sqrt do fator original); damping underwater idem.
- Moedas: oAnimState++ local retimado em três caminhos.
- Mario da abertura (Goddard): incrementos/decrementos de frame 1.0 -> 0.5; stillTimer 150/300 -> 300/600.
- APERTE START: fase visual deriva de (gGlobalTimer >> 1), mantendo gGlobalTimer em 60 Hz.
- Idle demo: 800 -> 1600 frames nativos.
- Logo inicial/TM: contadores visuais avançam em cadência legada de 30 Hz.
- Bob-omb chase: animFrame manual, giro e fuse timer retimados.

## Validação
- XEX final extraído com XexTool e mapped resultante idêntico byte a byte ao mapped planejado.
- Mapper de controles permaneceu byte a byte idêntico.
- Arquitetura segue 60 Hz nativos, sem segunda apresentação duplicada e sem interpolação do renderer.

## Item ainda em observação
A sobreposição/ghosting ocasional percebida no Mario na RC1 não é declarada resolvida nesta RC2. Esta revisão isola primeiro as correções de velocidade/timing. Se persistir, o próximo passo será o caminho visual de animação/presentação do Mario.
