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

## 07/10/2026 — levantamento estático do crawling concluído
- A fonte recuperada confirmou os pontos lógicos reais: `act_standing_against_wall()`, `push_or_sidle_wall()`, `act_crawling()` e `WallCollisionData/find_wall_collisions()`.
- A ação atual de mãos na parede sai quando recebe analógico; a nova mecânica deverá interceptar o botão de engatinhar nesse estado, guardar/recalcular a normal e executar uma ação de aderência separada.
- A ação de crawling normal já usa intenção do analógico, passo no chão e alinhamento ao piso; para o requisito do Pedro será necessário trocar o integrador por movimento projetado no plano tangente da normal, incluindo teto e superfícies inclinadas.
- IDs encontrados na fonte (não são endereços XEX): ACT_STANDING_AGAINST_WALL=0x0C400209, ACT_START_CRAWLING=0x0C008223, ACT_STOP_CRAWLING=0x0C008224, ACT_CRAWLING=0x04008448.
- Relatório publicado: docs/WALL_CRAWL_STATIC_SCAN_2026_10_07.md. Nenhum XEX foi alterado/liberado. Próxima ação: cross-reference desses pontos no PE/XEX e confirmação de ABI; só depois preparar um protótipo estático/emulado.

## 07/10/2026 — inventário automatizado do PE para candidatos de parede
- Foi criado `scripts/multilang/scan_wall_candidates.py`, que lê a tabela .pdata/.text do PE PowerPC e lista funções que acessam campos compatíveis com o estado de Mario.
- Execução na base `_localization_build/direct-jumps3.pe`: PASS, 665 candidatos amplos; relatório `docs/WALL_CRAWL_CANDIDATE_SCAN_2026_10_07.json`, SHA-256 `8a2a810554639f4d19af6c07856ae3e1d55db59ba6e3ff84a841f0d4d50b04cd`.
- Resultado não identifica ainda a rotina correta: o filtro por offsets de estado é amplo e não deve ser usado para patch. Nenhum XEX foi alterado.
- Próxima ação: refinar por sequência de acesso a `wall/floor/controller`, chamadas de colisão/passo e comparação de fingerprints da fonte; confirmar endereço e ABI antes de qualquer protótipo.
