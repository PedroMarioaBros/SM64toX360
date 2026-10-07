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


## 07/10/2026 — filtro refinado do PE sem candidato seguro
- O segundo filtro tentou combinar acesso a `m->wall`, campos de ação, posição e chamadas de função. Resultado: PASS técnico, zero candidatos seguros.
- Interpretação: os acessos do compilador usam registradores intermediários e o padrão simples por registrador não é suficiente para identificar `push_or_sidle_wall`/crawling. Isso evita um patch baseado em falso positivo.
- Arquivos publicados: `scripts/multilang/refine_wall_candidates.py` e `docs/WALL_CRAWL_REFINED_SCAN_2026_10_07.json`; SHA-256 do relatório: `d73507ab2f037ef67cbf7e416133323b7657d5c12d43ecb88ecb962ddd10c9d4`.
- Próxima ação: usar análise de fluxo de registradores/cross-reference de chamadas, ou localizar artefato de símbolos/mapa compatível, antes de qualquer XEX. Nenhum executável foi gerado.


## 07/10/2026 — busca externa por símbolos e artefatos
- Foram consultados repositórios e fontes públicas de porting/decompilação. `sirdankz/MKart360` confirma um fluxo público de build Xbox 360, mas é Mario Kart 64 e não fornece símbolos do nosso jogo. `TheGag96/sm64-port`/branch `extended_moveset` confirma as rotinas lógicas de parede/crawling, mas não contém crawling aderido nem mapa PowerPC/XEX compatível. `sm64-port/sm64-port` e doxygen fornecem nomes/relacionamentos, não endereços transferíveis. `ClementDreptin/XexUtils` é ferramenta geral, sem símbolos específicos.
- Nenhum mapa de símbolos, ELF/PDB, build reproduzível ou XEX público correspondente ao port/base v0.4 foi localizado. Relatório: `docs/EXTERNAL_SYMBOL_SEARCH_2026_10_07.md`.
- Não aplicar endereços externos por semelhança. Próxima ação: procurar commits/logs/branches específicos do port e continuar cross-reference local com fluxo de registradores.

## 07/10/2026 — arquivo sm64_dump.txt explicado
- Pedro encontrou `sm64_dump.txt` na pasta do jogo após desligar/fechar o console.
- O arquivo é um dump de diagnóstico gráfico da compilação de teste, não save nem asset do jogo. Cabeçalho: `SM64 360 FRAME DUMP`; tamanho observado 1.178.555 bytes; SHA-256 `93350c14d91f5908aa00bfe753e01ca79a20e4f0ba65492d5b9ddc7a52c1b703`; final: 2.027 chamadas `gfx_sp_tri1`.
- A origem está documentada em `docs/CONTROLES_XBOX360.md` e confirmada por `scripts/recovered/ptbr_0_4/controls_probe.py`: BACK+START solicita o dump gráfico. A compilação de diagnóstico pode gravá-lo após o flush no fechamento/retorno ao dashboard.
- Não incluir esse arquivo no pacote do jogo. Pode ser apagado manualmente sem afetar save/instalação. Para testes de produto, evitar BACK+START ou usar build sem diagnóstico. Relatório: `docs/SM64_DUMP_DIAGNOSTICO_2026_10_07.md`.
- Nenhum XEX foi gerado nesta análise. Próxima ação do projeto continua sendo cross-reference local da mecânica de wall-crawl e localização de amostras reais de dublagem; não retomar probes de seletor descartados.


## 07/10/2026 — escopo aprovado para o primeiro wall-crawl
- Após avaliar a dificuldade de qualquer superfície, o primeiro protótipo foi restringido a paredes verticais. Tetos, inclinações e transições ficam para depois de um teste estável.
- Contrato: mãos na parede + botão de engatinhar pressionado ativa aderência; analógico esquerdo sobe/desce/lateral; analógico direito continua somente câmera; soltar faz cair; contato inclinado rejeitado e física original preservada.
- Critérios incluem boot, menu/save, retorno após estrela, ausência de salto pelo analógico direito e queda normal ao soltar.
- Especificação publicada em docs/WALL_CRAWL_WALL_ONLY_SCOPE_2026_10_07.md. Nenhum XEX foi alterado. A próxima ação é cross-reference por fluxo de registradores/chamadas de colisão e harness estático; não entregar patch baseado nos 665 candidatos amplos.


## 07/10/2026 — pacote real de dublagem PT-BR recebido e BPS analisado
- Pedro forneceu SM64-PTBR-1.0-BMatSantos-Kosmus.zip (Library libfile_9e016d73140c8191990bad65594a864c) e https://www.romhacking.net.br/index.php?topic=1629.0. ZIP SHA256 6e85270ff7d694e0e14ce3f99e5e29cc290c480066602542104a72cee0aa07d1; patch SHA256 1a6a0d6acb3f9626d52ed8f6a71866007df059e494461984591887c509bef4a2.
- ZIP contém BPS, capa e dois leia-me; nenhuma amostra WAV/AIFF separada. Página confirma dublagem Mario/BMatSantos e Peach/Vihh_Art, edição Kosmus.
- CRC do patch validado. ROM fonte exigida: 8.388.608 bytes, CRC32 3CE60709; alvo 9.090.352 bytes, CRC32 AACB4011. Leia-me indica Super Mario 64 (U) [!].z64.
- Análise de proveniência reconstruiu 1.718.881 bytes sem fonte; 7.371.471 bytes permanecem dependentes da fonte. Dados parciais NÃO são ROM funcional; nenhum banco de voz identificado/decodificado, nenhum XEX gerado.
- Código: scripts/multilang/analyze_bps_partial.py; relatório docs/PTBR_BPS_ANALYSIS_2026_10_07.json. Próxima ação: obter do usuário ROM compatível ou já patchada, validar CRC, aplicar BPS e extrair bancos de áudio. Preservar tradução própria e não publicar ROM/áudio no repositório público. Crawling vertical segue pendente.
