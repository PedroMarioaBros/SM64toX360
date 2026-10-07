# Diagnóstico e pulos diretos — 07/10/2026

## Hardware
Pedro confirmou boot NOHOOK e PASSTHROUGH2. SELECTOR_TEST1 teve tela preta sem crash aparente. Não concluir que .lang foi acessada nem que gráficos/vozes/saves passaram, pois os diagnósticos não exercitam essas rotinas.

## Verificações desta sessão
- Capstone confirmou destinos reais init_rcp 0x820CE780, render_game 0x82099498, ortho 0x820D0470, print_generic_string_fade 0x82143110.
- Alpha usado pelo print é 0x82E52F88 menos 0x82E52F8B; o gate escreve nos endereços corretos.
- alloc_display_list 0x820FB8A0 usa pool dinâmico em 0x82E47B14; setup frame 0x820CC958 reseta esse pool antes do hook. Falha por pool nulo em emulação sem setup NÃO demonstra falha real do Xbox.
- Descritores XEX: base 251 páginas (3:9,1:51,2:191); diagnóstico expandido 262 (3:9,1:51,2:202). Páginas novas herdam tipo 2. Não há evidência nesta sessão de que isso cause falha.
- Harness test_pregame_gate.py PASS, mas simula chamadas externas; não usar como prova gráfica.
- Probe com código real, memória de gráficos sintética e modelagem de std/ld, extsw, fcfid e floor/ceil em Unicorn32 atravessou render, ortho e impressão de créditos. Parou na finalização com escrita não mapeada em 0x820CE6D8 porque estruturas de tarefa gráfica não foram inicializadas. Esse teste parcial NÃO prova execução em console nem causa da tela preta. Não repetir probe sem incluir setup de tarefa.

## Pulso A/B/Y solicitado
A preserva pulo normal e sequência original. B aciona segundo pulo diretamente do chão, inclusive parado. Y aciona terceiro pulo diretamente do chão, inclusive parado. Não é um salto extra no ar. X continua ataque. Sem alterar base 30 FPS.
Mapper 0x82165998: B livre; Y bloco 0x82165A50..0x82165A78 alterna skip_decals, não FPS nesta base. Estado XInput atual em stack+0x54; anterior 0x82F9E364 atualizado em 0x82165A80. Capturar borda B/Y antes dessa atualização, sem repetir ao segurar.
set_mario_action identificado em 0x820DE350: r3 MarioState, r4 ação, r5 argumento; chama setup aéreo 0x820DDC50 para grupo air. ACT_DOUBLE_JUMP 0x03000881; ACT_TRIPLE_JUMP 0x01000882. Chamar essa rotina, não apenas sobrescrever velocidade ou altura.
Validar endereço MarioState, ponto de consumo após atualização de inputs, estados válidos do chão, segurar B para altura normal do segundo pulo (flag CONTROL_JUMP_HEIGHT depende de input A_DOWN), prioridade botões simultâneos e ausência de salto em menus/cutscenes/água antes de empacotar.
Ainda não há patch de pulos ou seletor corrigido implementado/validado. Não gerar candidato com código incompleto.

## Próximo bloco concreto
1. Completar teste de gate com setup gráfico real ou diagnóstico que exercite leitura/escrita .lang separado do render; não repetir boot NOHOOK/PASSTHROUGH.
2. Localizar ponto de execução Mario após input e implementar atalhos usando set_mario_action, cobrindo parado/correndo, borda de botão, A original e Y sem sombras.
3. Só então reconstruir/verificar round-trip e entregar candidato com checklist real. Registrar pendências se algum componente não puder integrar.
