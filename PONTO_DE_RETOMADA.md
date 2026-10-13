# Ponto de retomada — leia primeiro
Branch ativa feature/multilang-dub-30fps; base30FPS. Leia AGENTS.md e CHECKPOINT_PROJETO.md.

**TEST3 aprovado novamente em hardware**, inclusive retorno após estrela sem crash, em 12/10/2026. **CREDITS_MENU_CORRIGIDO FALHOU em gameplay (Fatal Crash após estrela); NÃO é versão estável.** Prioridade agora textos equivalentes PT-BR / ES / EN e botões Xbox nos três; dublagem adiada.

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

## 07/10/2026 — sm64_dump.txt identificado
- Dump gráfico de diagnóstico, não save/asset. SHA-256 93350c14d91f5908aa00bfe753e01ca79a20e4f0ba65492d5b9ddc7a52c1b703; 1.178.555 bytes; 2.027 chamadas gfx_sp_tri1.
- Origem confirmada: BACK+START solicita o dump na compilação de diagnóstico. Relatório: docs/SM64_DUMP_DIAGNOSTICO_2026_10_07.md.
- Não incluir no pacote; pode ser removido manualmente sem afetar save. Próxima ação: wall-crawl/dublagem, sem repetir probes descartados.


## 07/10/2026 — wall-crawl vertical como primeiro escopo
- Protótipo restrito a paredes verticais; botão de agachar mantém aderência, analógico esquerdo move, soltar faz cair; câmera/A-B-Y preservados.
- Especificação: docs/WALL_CRAWL_WALL_ONLY_SCOPE_2026_10_07.md. Nenhum XEX alterado; próxima ação é cross-reference e harness estático.


## 07/10/2026 — pacote real de dublagem PT-BR recebido e BPS analisado
- Pedro forneceu SM64-PTBR-1.0-BMatSantos-Kosmus.zip (Library libfile_9e016d73140c8191990bad65594a864c) e https://www.romhacking.net.br/index.php?topic=1629.0. ZIP SHA256 6e85270ff7d694e0e14ce3f99e5e29cc290c480066602542104a72cee0aa07d1; patch SHA256 1a6a0d6acb3f9626d52ed8f6a71866007df059e494461984591887c509bef4a2.
- ZIP contém BPS, capa e dois leia-me; nenhuma amostra WAV/AIFF separada. Página confirma dublagem Mario/BMatSantos e Peach/Vihh_Art, edição Kosmus.
- CRC do patch validado. ROM fonte exigida: 8.388.608 bytes, CRC32 3CE60709; alvo 9.090.352 bytes, CRC32 AACB4011. Leia-me indica Super Mario 64 (U) [!].z64.
- Análise de proveniência reconstruiu 1.718.881 bytes sem fonte; 7.371.471 bytes permanecem dependentes da fonte. Dados parciais NÃO são ROM funcional; nenhum banco de voz identificado/decodificado, nenhum XEX gerado.
- Código: scripts/multilang/analyze_bps_partial.py; relatório docs/PTBR_BPS_ANALYSIS_2026_10_07.json. Próxima ação: obter do usuário ROM compatível ou já patchada, validar CRC, aplicar BPS e extrair bancos de áudio. Preservar tradução própria e não publicar ROM/áudio no repositório público. Crawling vertical segue pendente.


## 08/10/2026 — avanço: localização do áudio no BPS
- Rastreamento executado: CTL original 0x57B720 → alvo 0x57F8D0; TBL original 0x593560 → alvo 0x597710. Não aplicar offsets originais ao alvo traduzido.
- CTL de 97.856 bytes: 3.348 conhecidos diretamente pelo patch, 94.508 dependem da fonte. Primeiro bloco de 512 bytes inteiramente desconhecido. Ainda sem banco completo ou voz decodificada; nenhum XEX alterado.
- Código scripts/multilang/map_bps_audio_anchors.py; relatório docs/PTBR_AUDIO_OFFSETS_2026_10_08.md na branch ativa.
- Pedro não possui ROM. Próxima ação: comparar tabelas e amostras originais do XEX base do projeto com dependências do patch, completando somente bytes com correspondência comprovada; alternativa é pacote de vozes dos autores. Não inventar bytes nem declarar áudio completo usando saída esparsa. Crawling vertical segue pendente.

## 09/10/2026 — ponto de continuidade da dublagem (código na branch ativa)
- Foi concluída a auditoria forense BPS × XEX com o patch PT-BR fornecido e `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip` recuperado. XEX Basic descriptografado com PE válido de 17.170.432 bytes; comparação amostrada: 853 probes de 16 bytes, 853 de 32 e 800 de 64, **0 hits exatos**.
- Código testado (4 testes locais PASS), relatórios, hashes e workflow de CI na branch **`feature/multilang-dub-30fps`**: `scripts/multilang/audit_bps_xex_overlap.py`, `scripts/multilang/test_audit_bps_xex_overlap.py`, `docs/PTBR_XEX_AUDIO_AUDIT_2026_10_09.md` e `.json`.
- **Próximo passo:** investigar layout e metadados dos soundbanks internos do XEX, procurando correspondências estruturalmente verificáveis com CTL/TBL; não preencher lacunas com bytes presumidos. Não há voz extraída ou XEX novo. Base 30 FPS preservada. Ver checkpoint da branch ativa para detalhes.


## 09/10/2026 — continuidade VADPCM na branch ativa
- **NOVA trilha validada:** patch BPS contém quadros VADPCM (62/71 trechos longos com 100% de headers em uma fase de 9 bytes), e PE Xbox 360 contém codebooks VADPCM completos e quadros de áudio compatíveis (452 candidatos de livro). Nenhuma das 43 janelas parciais de coeficientes do patch corresponde exatamente às candidatas Xbox. Não há áudio dublado extraído.
- Código, testes e evidências estão em `feature/multilang-dub-30fps`: [relatório 09/10](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/PTBR_VADPCM_STRUCTURAL_AUDIT_2026_10_09.md). Workflows de testes: [scanner PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37958461771), [XEX PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37958879757).
- Próxima ação: localizar referências reais e associar samples/codebooks aos IDs das vozes do Mario/Peach; sem XEX especulativo, sem alterar 30 FPS, saves ou tradução canônica.

## 09/10/2026 — marco da recuperação de áudio PT-BR (branch ativa)
- **4 WAVs experimentais privados** gerados a partir do BPS do usuário e dos bancos CTL/TBL originais recuperados do XEX. Eventos: banco 08 slots 04 (Yahoo) e 06 (Hrmm); banco 0A slots 02 (Panting) e 09 (Punch Yah).
- Banco original do XEX indexa 38 CTL e 38 TBL, incluindo **50 amostras de vozes originais**; slot físico 03 no banco 0A é nulo.
- A reconstrução parcial **não comprova CRC da ROM N64 fonte**: conhecidos no BPS 3.361.841 bytes, lacunas CTL 905 bytes e TBL 316 bytes. WAVs precisam de validação auditiva; 46 outros eventos não disponíveis para exportação estrita. Nenhum novo XEX.
- Documentação e código [relatório ativo](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/PTBR_VOICE_RECOVERY_2026_10_09.md), [reprodutor](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/scripts/multilang/reconstruct_ptbr_audio_from_xex.py), [6 testes PASS no CI](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37966469573).
- Pacote privado das 4 prévias está salvo na Biblioteca do projeto em `/Xbox360 - SM64 PTBR/SM64_PTBR_4_PREVIAS_EXPERIMENTAIS_2026-10-09.zip`, ID `libfile_e46daa6cc8788191ba06e1cf87af923c`.
- **Próximo passo real:** confirmar escuta e mapear proveniência das lacunas para ampliar samples sem inventar bytes. Preservar base 30 FPS, controles, saves e tradução.


## 09/10/2026 — CHECKPOINT MAIS RECENTE: seis WAVs experimentais na branch ativa
- Branch `feature/multilang-dub-30fps`: **6 prévias de vozes PT-BR experimentais**; quatro com todos os metadados exigidos completos e mais duas com dados VADPCM/codebook completos mas cabeçalho de loop incompleto (08/16 Mario So Longa Bowser; 0A/04 Mario Dying). Saídas PCM Python e C equivalentes. Ainda sem aprovação por escuta, sem ROM fonte CRC-validada e sem novo XEX.
- Corrigida recuperação de **64 bytes zero de padding CTL** e **16 bytes zero de padding TBL** observados diretamente no PE: **3.361.921 bytes conhecidos** no BPS parcial. Restam **841 bytes desconhecidos no CTL** e **316 bytes no TBL**; todos remetem a offsets da ROM fonte fora dos bancos de áudio recuperados.
- Relatório e código: [seis WAVs](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/PTBR_SIX_VOICE_PREVIEWS_2026_10_09.md), [lacunas BPS](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/PTBR_BPS_AUDIO_GAPS_2026_10_09.md), [scanner de dependência](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/scripts/multilang/trace_audio_dependency_gaps.py), [decodificador sem loop](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/scripts/multilang/decode_vadpcm_without_loop.py).
- Testes reais no GitHub Actions: [rastreio 4 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37967913594) e [decodificador 11 PASS, 5 novos](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37968449638).
- ZIP privado consolidado de 6 WAVs, 459.699 bytes: Biblioteca `/Xbox360 - SM64 PTBR/SM64_PTBR_6_PREVIAS_EXPERIMENTAIS_2026-10-09.zip` (libfile `libfile_986a0b2fe0b88191aa466ed03292d4ec`), SHA-256 `cfc024aac266f5da8905e38139f6e7ba01762af5b8738735686cd917d7f79a10`. Não há binário/áudio publicado no GitHub público.
- Continuação: ouvir/identificar as seis prévias, buscar bytes faltantes por origem comprovável; não fabricar vozes nem alterar base estável de 30 FPS/PT-BR/saves/canhão.


## 12/10/2026 — URGENTE: crash reproduzido ao voltar da estrela; versão de créditos NÃO estável
- Feedback real de Pedro após novo teste no Xbox: `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip` exibe letras e menu corretamente, mas **Fatal Crash ao pegar estrela e voltar ao castelo**. Revogada aprovação geral da build; apenas render do menu passou.
- Análise exata dos XEXs recuperados: o PE falho difere da TEST3 **somente** pelo branch em `0xCD128` (`4bfc8321` → `482ef7d9`) e code cave de créditos `0x3BC900..0x3BCA08`. **226 bytes diferentes; rollback desses dois intervalos gera PE byte-idêntico ao TEST3**.
- Enviado arquivo A/B `SM64_30FPS_TESTE_ISOLAMENTO_CRASH_ESTRELA_TEST3.zip` que encapsula `default.xex` TEST3 original *sem recompilar*, SHA-256 ZIP `02df1f67fba83e9d1cdd5f60ef3924f4fc48c58adb4555b372e69f2270d39893`, Biblioteca `libfile_0b550c3cf5b481919d988f4e302fc2c5`. OBJETIVO: verificar no Xbox se TEST3 também falha na transição estrela→castelo. **Resultado de console ainda pendente.**
- Relatório/código ativo: [STAR_RETURN_CRASH_2026_10_12.md](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/STAR_RETURN_CRASH_2026_10_12.md). [GitHub Actions 4 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38205019787), somente validação estática do isolamento, não emulação do ciclo completo.
- Não criar XEX especulativo. Após A/B, corrigir fluxo do menu/créditos sem hook global persistente; garantir coleta de estrela, retorno ao castelo, menu e save antes de integrar o áudio.
- Áudio: seis WAVs PT-BR experimentais preservados, ainda sem aprovação por escuta ou XEX com dublagem. Base canônica 30 FPS/PT-BR/controles permanecem.


## 12/10/2026 — DIREÇÃO NOVA E PROGRESSO TRILÍNGUE (branch feature/multilang-dub-30fps)
- Pedro confirmou **TEST3 PASS real no Xbox**, inclusive estrela→castelo; versão de créditos/menu posterior tem Fatal Crash após estrela. Não reutilizar hook global de `level_script_execute` / offset `0xCD128`.
- **Prioridade do proprietário alterada:** PT-BR / Español / English com textos **equivalentes em significado** e controles Xbox 360 nos três. **Dublagem adiada.** PT-BR da PMCN Studios canônico, intocável; EN original com botões Xbox; ES de fonte existente com revisão.
- Fonte EN `n64decomp/sm64@9921382a` e ES `Reonu/ultrasm64-spanish@b720e832` processadas, **170 diálogos por idioma**. Correções semânticas ES #015, #030, #032, #034, #046; 34 diálogos de controle Xbox cobertos; nenhum token N64 restante nos diálogos. PT-BR não modificado.
- Novo importador EN/ES para **15 fases/90 missões/10 entradas secretas** mais textos auxiliares; erro ortográfico ES "ISLA FLOANTE" corrigido. Catálogo gerado em `_localization_build`, mas ainda não integrado ao runtime do Xbox. Não confundir processamento de fonte com entrega de XEX.
- [GitHub Actions trilingual text audit **18 testes PASS** + fontes reais EN/ES e alinhamento de IDs PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38333296556); script `scripts/multilang/audit_language_parity.py`; [relatório completo](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TRILINGUAL_TEXT_PARITY_2026_10_12.md).
- **Pendências:** revisão editorial completa das informações, integrar nomes de fase e UI/menus, seletor de idioma na introdução por caminho seguro sem hook de créditos causador do crash, XEX rastreável e validação real incluindo retorno de estrela/save em cada idioma. Nenhum novo executável multilíngue foi entregue.


## 12/10/2026 — AVANÇO MULTILÍNGUE: POINTERS REAIS E PPC EMULADO (CONSULTAR BRANCH FEATURE)
- A TEST3 validada por Pedro no console (incluindo estrela→castelo) **já contém uma seção .lang com 170 diálogos em PT-BR, ES e EN** e os glifos ES. Ela não os alterna em gameplay porque falta um seletor/ativação segura. Além disso, a versão ES já inserida está defasada das erratas de equivalência feitas em 12/10 (ex. diálogo 015 sem chute A+X).
- Verificados no PE TEST3, sem modificar XEX: tabela real de 26 nomes de áreas `0x9E8C70` (SHA-256 ponteiros `3b789baca2d6d547c0f8f2985e96da24b4878944c1278d092c614d53934cbc9d`) e 90 nomes de estrelas `0x9E9620` (SHA-256 `ed5c7e598cade70bcfda05d3293b230a449650f9b45bf1f52572749640be30b0`); PT-BR preservado.
- `.lang` v2 usada `0x18D4E` / capacidade `0x20000`, **29.362 bytes livres** para anexar curso/missões ES/EN e diálogos revisados, sob guarda de capacidade. Os nomes de curso PTBR estão preservados por ponteiros originais; as tabelas ES/EN dependem dos catálogos já processados.
- Novas ferramentas na branch ativa: `scripts/multilang/install_trilingual_course_tables.py` (monta COURSE3 26+90 tabelas PT/ES/EN sem tocar gameplay), `scripts/multilang/course_table_activation.py` (PowerPC 148B de seleção 26+90; sem hook instalado), `scripts/multilang/patch_existing_lang_dialogs.py` (anexa somente diálogos ES/EN alterados, bloqueia qualquer mutação do PT-BR).
- [7 testes de estrutura/segurança PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334053320), [5 cenários PowerPC Unicorn PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334216661), [6 testes de delta ES/EN PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334793668). Relatório completo [TRILINGUAL_COURSE_RUNTIME_2026_10_12.md](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TRILINGUAL_COURSE_RUNTIME_2026_10_12.md).
- **Nenhum novo XEX testável nesta sessão**: ainda falta anexar os catálogos e correções ES/EN reais, integrar menus, ligar a seleção na rotina legítima da intro (não hook global do level_script_execute, que causou Fatal Crash), compilação XEX e teste de retorno ao castelo nos três idiomas. Dublagem continua adiada.


## 12/10/2026 — TEST3: DADOS PT/ES/EN REAIS INTEGRADOS, SEM XEX AINDA
- Na branch `feature/multilang-dub-30fps` foi usado PE mapeado real da TEST3 aprovada no Xbox. Resultado `96abbfb76775f4184b24106c1b78a1409ac1d9ace8bf5fa61a98af76a1b9eed8` (SHA-256) com 26 nomes de áreas e 90 estrelas por idioma, **20 diálogos ES corrigidos** e os 170 EN/170 PT-BR originais intocados. **13.841 bytes livres em .lang**; todas as instruções fora da seção continuam idênticas à TEST3, inclusive ganchos anteriormente problemáticos.
- Material intermediário recuperável na Biblioteca privada `/Xbox360 - SM64 PTBR/SM64_TEST3_TRILINGUAL_DATA_STAGING_PRIVADO_2026-10-12.zip`, id `libfile_d1affc8caa3c819193c8e2db0f6bb29e`, SHA `dec42ea2228d0b52e16ec900f1314fe8fbc66da241e9ecde723abdf2c5af6c6c`, 7.414.645 bytes. Contém PE e relatórios, **NÃO é XEX e NÃO é jogável**.
- Foi corrigido bug real da serialização JSON dos sete `EXTRA_TEXT`, após primeira falha segura de integração; [testes CI PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38335811493).
- [Relatório e hashes detalhados](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TRILINGUAL_REAL_TEST3_STAGING_2026_10_12.md). Próximo: seletor na introdução sem hooks anteriores, menus completos, XEX e testes estrela→castelo/save nos três idiomas. PT-BR canônico preservado, dublagem adiada.

## 12/10/2026 — DUBLAGEM FORMALMENTE FORA DO ESCOPO ATUAL (REGRA DO PROPRIETÁRIO)
- Instrução explícita: **NÃO trabalhar na dublagem** — sem extração, tratamento, integração, novos testes ou builds de vozes — até que a edição única de Super Mario 64 Xbox 360 esteja **plenamente funcional com as traduções Português / Español / English e com a tela de seleção de idioma realmente funcional no Xbox 360**.
- Cada idioma precisa preservar conteúdo equivalente e comandos Xbox 360 corretos. Validar no hardware boot, seletor, menus, diálogos, placas, fases/estrelas, saves e ciclo estrela→castelo sem crash **nos três idiomas**.
- Preservar os áudios originais já existentes na TEST3; a proibição se refere a desenvolvimento/alterações de dublagem, não a silenciar sons nativos.
- Os arquivos WAV anteriormente recuperados continuam arquivados, mas **não integram o escopo nem a sequência de implementação**. Só voltar a considerar dublagem se (1) todos os requisitos acima forem comprovados por testes no Xbox e (2) houver nova autorização expressa do proprietário, jamais automaticamente.
- Manifesto de política detalhado na branch ativa: `localization/manifests/languages.json` (`dubbing_policy.status = blocked_not_in_current_project_scope`).
- Último estado: TEST3 real com dados PT/ES/EN preparados em PE intermediário privado, **seletor e XEX trilíngue ainda não funcionais no console**. Prioridade exclusiva: terminar traduções, interface, seleção e validação.


## 12/10/2026 — TEST4 XEX EXPERIMENTAL GERADO PARA TESTE REAL NO XBOX (SELETOR PT/ES/EN)
- **NOVA VERSÃO REAL DISPONÍVEL, MAS HARDWARE AINDA NÃO TESTADO:** `SM64_TEST4_SELETOR_TRILINGUE_30FPS_TESTE_XBOX.zip`, ZIP SHA-256 `3d1bd3ad11a49d88e0a742586e6b55cd202b4e4ad93fcb36719b7ea22b7405f8` (17.185.690 B), inclui `default.xex`, README e auditoria. **XEX SHA-256** `ae43067a1849d115a591c163df4f942e8f3f7a40e83a69029fac69dadd0920be` (17.182.720 B). **PE round-trip AES exato PASS**, SHA `10549edf9a516b6b7099034519ea5973ed0ad989042d7a25a5b74155a1f729e1`. ZIP CRC PASS.
- **BACKUP PRIVADO** `/Xbox360 - SM64 PTBR/SM64_TEST4_SELETOR_TRILINGUE_30FPS_TESTE_XBOX.zip`, Library `libfile_abecdb8e5ef081919667d1a3127f7ee7`. Não subir XEX/PE público no GitHub.
- **CONFLITO CRÍTICO RESOLVIDO:** direct_jumps B/Y armazena entradas em `.lang+0x80/+0x84`, que antes estavam sendo sobrescritas pelo cabeçalho `COURSE3` nos scripts de áreas. Movido `COURSE3` para `.lang+0xC0..0xF3` e atualizada ativação de áreas (`+0xD8`) e estrelas (`+0xE4`); imagem de dados segura SHA `df139691efb4d146aca07215fa7becf3164a68ad4b778cadd575cd5ef04dfc76`. Regressões sintéticas B/Y, cursos e PowerPC PASS ([CI cursos](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337827003)).
- **SELETOR LIGADO SOMENTE AO TÍTULO:** fonte `scripts/multilang/title_only_selector.py`; desvio BL nativo `0x820D68BC` (CALL de `intro_regular` exclusiva da ramificação LVL_INTRO_REGULAR) para wrapper `0x823BC900` **492 bytes** SHA `66d84fb375d527d7d600595c3fe070461540820630d06aa205802b8a5a44a02f`; ativação diálogos 88B em `0x823BC800` e cursos+estrelas 148B em `0x823BCC00`. **572 bytes efetivamente alterados** entre PE de dados seguro e candidato, somente as três caves vazias e BL de título. `level_script_execute` original em `0x820CD128` e entrada antiga `intro_regular` `0x820D5F48` **INTOCADOS**. Cuidado: não reutilizar outros hooks que crasharam.
- **FUNCIONAMENTO PROJETADO:** após créditos do jogo, tela inicial apresenta `IDIOMA / LANGUAGE`, `Português`, `Español`, `English` com cursor; D-pad UP/DOWN escolhe e A confirma; START fica bloqueado durante escolha; depois de A o START original abre saves; 170 diálogos, 26 nomes de áreas e 90 estrelas recebem as tabelas selecionadas. Conferir aparência/render em console antes de declarar funcional.
- **TESTES:** [test-title-only-selector CI 38337494648](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337494648) PASS: emulação PPC de D-pad, A selecionando cada um dos 3 idiomas com escrita real de ponteiros, Start antes/depois, preservação B/Y e registros. [Host xex2replace CI 38337505562](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337505562) PASS; rebuild XEX e roundtrip local exato PASS. **Não há prova de GPU/boot no Xbox nesta TEST4.**
- **TESTE PEDRO:** colocar em pasta SEPARADA, preservar TEST3/save backup. Verificar 1) boot e tela da escolha, 2) UP/DOWN, A, Start → saves; 3) tradução diálogo/fase/estrela; 4) obter estrela e voltar ao castelo; 5) salvar/carregar; repetir nos 3 idiomas. Se falhar, registrar a etapa/tela exata, especialmente Fatal Crash. Não marcar TEST4 estável antecipadamente.
- **PENDÊNCIAS:** menu de saves/outros textos da UI ES/EN ainda não plenamente localizados; revisão editorial integral de equivalência entre idiomas pendente; funcionamento GPU/tela/save e estrela→castelo nos 3 idiomas pendente. **DUBLAGEM TOTALMENTE FORA DE ESCOPO** e NÃO retomar sem aprovação explicitamente renovada após jogo trilíngue estabilizado e seletor funcional.
- **RELATÓRIO:** [docs/TRILINGUAL_TITLE_TEST4_REAL_XEX_2026_10_12.md](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TRILINGUAL_TITLE_TEST4_REAL_XEX_2026_10_12.md). Branch ativa `feature/multilang-dub-30fps`, 30FPS.


## 13/10/2026 — TEST4 SEM SELETOR NO XBOX; TEST5 XEX CORRIGIDA GERADA (AGUARDA TESTE REAL)
- **Resultado de hardware informado por Pedro:** a TEST4 abre, créditos iniciais PASS, tela Aperte Start normal **SEM seletor**, menu de saves e jogo PT-BR abrem normalmente. **Reprovação do requisito principal**: o seletor de idiomas não aparece; não alegar que a TEST4 é multilíngue funcional. Não foi relatado teste de retorno após estrela na TEST4.
- **Falha localizada COM DESASSEMBLAGEM REAL:** a TEST4 alterou `0x820D68BC`, que pertence a **outro menu**, e não ao `lvl_intro_update` da tela de título. No PE TEST3/TEST4, o dispatcher real `lvl_intro_update` está em `0x82147408` e tem quatro BLs originais: `0x82147434`=greeting, **`0x82147448`=`intro_regular` (código `4bfffe31`, destino `0x82147278`)**, `0x8214745C`=gameover e `0x82147470`=level-select. Esse erro de endereçamento explica a ausência do seletor mesmo com testes isolados do wrapper PASS.
- **Correção no código GitHub:** `scripts/multilang/title_only_selector.py` agora aponta para `CALLSITE=0x82147448` / `ORIGINAL_INTRO=0x82147278`; `verify_native_title_dispatch` bloqueia chamadas divergentes e detecta patch errado TEST4. Regressão em `test_title_only_selector.py`; [CI 38415812279 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38415812279) com artefatos PPC atualizados.
- **Nova TEST5 XEX BASIC REAL gerada:** `SM64_TEST5_SELETOR_TRILINGUE_TELA_INICIAL_30FPS.zip`, CRC ZIP PASS, 17.184.588 B, SHA-256 ZIP `4e28d292b8e50066e0e903c0ea310b053b2b5843fdb549068c197b8f70d3d8fc`. `default.xex` 17.182.720 B SHA-256 **`386a1516ee9a1da3475ac008dd3ddda4bf13fd92c779e38f6cafc038217ab7b6`**. PE reconstruído SHA `a6c0a1c451f6dd114f73bd324cb297d42f3ed6f6c027c8237d3244284e622672`. **Roundtrip reconstrução XEX→PE exato PASS**.
- **Apenas 14 bytes efetivamente diferentes TEST4→TEST5**: restaurou `0xD68BC` como original, instalou BL correto `482754b9` em `0x147448`, atualizou duas BL internas do wrapper `0x3BC900`. Toda seção `.lang`, 170 diálogos por idioma, 26 fases+90 estrelas por idioma, 30FPS, PTBR, B/Y, saves e `level_script_execute` originais **byte-idênticos** à TEST4. Nenhum conteúdo de dublagem alterado.
- **Arquivo preservado em Biblioteca privada:** `/Xbox360 - SM64 PTBR/SM64_TEST5_SELETOR_TRILINGUE_TELA_INICIAL_30FPS.zip`, Library `libfile_7af70f58d3ec819189934e882f1fc729`. Não publicar XEX no repo público.
- **CRÍTICO: TEST5 AINDA NÃO FOI TESTADA NO XBOX REAL.** Pedro deve extrair em pasta separada sem apagar TEST3/saves e confirmar primeiro tela Português/Español/English após créditos. Se abrir e navegar A, depois Start/saves, textos de idioma e pegar estrela→castelo. Se tela não aparecer, revisar renderização `print_generic_string_fade` no contexto título e caminho de chamada. Não inventar progresso.
- **Relatório:** [docs/TEST4_SELECTOR_MISSING_TEST5_CORRECTED_2026_10_13.md](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST4_SELECTOR_MISSING_TEST5_CORRECTED_2026_10_13.md).
- **Dublagem formalmente fora do escopo.** Nenhum trabalho com vozes antes de PT/ES/EN completos, seleção funcional e aprovados no Xbox, seguido de nova instrução explícita.
