# Ponto de retomada — leia primeiro
Branch ativa feature/multilang-dub-30fps; base30FPS. Leia AGENTS.md e CHECKPOINT_PROJETO.md.

Aprovados Xbox: pulos TEST3/câmera, RENDER90, TEXTO90, CREDITS_MENU_CORRIGIDO com menu/save. Preserve.

TITLE_SELECTOR_TEST1 reprovado: não alterou a tela Press Start e causou travamento após pegar estrela/retornar ao castelo. Não reutilizar 0x820D5F48; candidato retirado.

Direção permanece: créditos universais → verdadeira rotina Press Start pós-créditos → seletor → créditos personalizados → menu saves. Próxima ação é cross-reference real de lvl_intro_update/intro_regular e contrato de retorno. Nenhum novo XEX até confirmação.

[Checkpoint](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/CHECKPOINT_PROJETO.md)


## 07/10/2026 — novo requisito: crawling aderido a qualquer superfície + investigação de dublagem
- Pedro confirmou a mecânica desejada: ao encostar na parede e manter o botão de engatinhar/abaixar pressionado, Mario deve aderir à superfície e se mover com o analógico esquerdo em todas as direções. A direção deve ser projetada no plano tangente da normal da superfície, incluindo paredes verticais, inclinadas e teto; ao soltar, desanexar conforme a física (cair ou permanecer quando a superfície sustentar).
- Este requisito ainda não está implementado nem testado. Próxima ação técnica: localizar a ação/estado de hands-on-wall, a normal de colisão e o integrador de movimento no XEX; criar primeiro uma especificação/scan estático, sem entregar XEX especulativo. Preservar A/B/Y, câmera, 30 FPS, menu, saves e PT.
- Dublagem: a investigação remota confirmou que os repositórios públicos identificados são fontes de código/definições, não pacotes de áudio prontos. `bMatSantos/sm64-ptbr` expõe a árvore `sound/` com README, sequências e bancos JSON, mas não foram encontrados arquivos de amostras de voz; `Reonu/ultrasm64-spanish` expõe `sound/sequences/` e `sound/sound_banks/` JSON, também sem amostras AIFF/ADPCM no conteúdo consultado. O README do projeto espanhol documenta que amostras seriam arquivos AIFF comprimidos no processo de build. Não declarar que os arquivos de dublagem foram recuperados.
- Estado da dublagem: bloqueado até localizar um pacote/release que contenha as amostras ou obter autorização/arquivos dos autores. Não integrar silêncio ou substituir vozes originais sem decisão registrada.
- Não repetir probes de seletor pré-créditos nem reutilizar 0x820D5F48; essa linha continua encerrada.