# Continuidade canônica — SM64 Xbox 360
Atualizado: 09/10/2026. Repositório: PedroMarioaBros/SM64toX360.
Branch de desenvolvimento: feature/multilang-dub-30fps.

## Como retomar
1. Ler este arquivo e AGENTS.md antes de editar ou reconstruir.
2. Consultar os arquivos técnicos na branch de desenvolvimento; main é também entrada para descoberta.
3. Ler docs/PREGAME_GATE_STATIC_INTEGRATION_2026_10_05.json e os scripts citados abaixo.
4. Conferir a revisão remota e diferenças locais. Não repetir recuperação ou testes já comprovados sem motivo.
5. Próxima ação: preparar seletor completo sobre render/texto aprovados; preservar pulos TEST3. Atualizar este checkpoint após cada resultado relevante e antes de encerrar.

## Objetivo e decisões permanentes
Edição única baseada na v0.4 funcional de 30 FPS, com seleção Português / Español / English antes de qualquer tela normal.
PT-BR: preservar exatamente a tradução existente do usuário e comandos Xbox 360; posteriormente dublagem PT-BR.
ES: tradução completa, comandos Xbox 360 e posteriormente vozes espanholas.
EN: textos e vozes originais, com TODAS as referências a controles localizadas para Xbox 360.
Crédito: PeterKleizoon - PMCN Studios.
Não misturar Native60, não substituir PT-BR pela tradução pública BMatSantos, não usar o grande BSS de .data para os pools.
Nenhum teste estático ou em Unicorn equivale a funcionamento comprovado no Xbox.

## Onde estamos
STATUS: RENDER_90 e TEXTO_90 aprovados no console, incluindo jogo e continuidade de save existente; seletor completo ainda pendente.
Novo candidato SELECTOR_TEST1 reconstruído, validado e disponibilizado para primeiro teste no console.
Os hashes históricos EN/ES seguem sem reprodução; essa pendência de rastreabilidade não foi declarada resolvida. O novo candidato foi validado independentemente com fontes fixadas, layout, ponteiros, preservação PT e round-trip.
Teste real de 06/10: SELECTOR_TEST1 ficou em tela preta; não abriu o jogo e não houve crash aparente. O seletor não foi alcançado. Próximo requisito: isolar expansão XEX versus gate.
Menus/cursos/estrelas completos e dublagens PT/ES ainda pendentes.
Não usar percentuais aproximados de conversa como evidência de conclusão.

## Bases e hashes
- sm64corrigido.xex: 6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8
- v0.4 PT-BR XEX: 376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83
- v0.4 mapped, 16.449.536 bytes: 6381bf1333bf1985474af00c139f33f9cdbad71a371c3231db0d861b72cfac2c
- PT pool, 26.044 bytes: 0b913e5c728f3991c8885df8b4b262b9f68de54cce5b485e46fa101765a84c9a
- Gate, 596 bytes: 27005f5c6ed015e7bbc75263a125ccc21c2eab099a0a65411141fb3b999be3aa
- XEX integrado de análise: 1792f578ea46d9fafe2676fdd2f97994c4057524edb11eb5b2d913acae7de5e9
- PE integrado: 315498a8ca65cbff54d83b9654b9c6fe7fe2efa4f66ae7aee2dfeecddab04769

## Evidências atuais verificadas no relatório remoto em 05/10
- [x] 510/510 ponteiros válidos.
- [x] 170 diálogos PT-BR byte a byte idênticos.
- [x] Zero bytes alterados fora das regiões previstas.
- [x] Round-trip XEX → PE byte a byte idêntico.
- [x] Workflow de teste do gate registrada: https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37271932321
- [x] Gate sem placeholders; créditos ~45 frames, A adianta; seletor D-pad e A; depois delegação ao script original.
- [ ] Confirmar comportamento real do render, controles, áudio e saves no Xbox 360.

## Divergência histórica preservada (não é o pool do novo candidato)
| Pool | Esperado no checkpoint | Atual no relatório |
| --- | --- | --- |
| EN bytes | 33955 | 33955 |
| EN SHA-256 | 819dba9fa68d2db08edc27f2ce05532bdfc734dd1a3a24754ab51abff3479f29 | b3c807d352381f5db555dcbb50fa3df858b671d66c43fd308ac4f375ccecba34 |
| ES bytes | 39173 | 39189 |
| ES SHA-256 | 361bce11e893615be1bdcca5699dd863db84fdd31091f1763f6f2f3059d35685 | fd8bebe9d2aa1f2a930962a93466552483f8be05e620d0ed1252cc5d311295de |

Comparar fontes, normalização de controles, codificação e glifos; registrar diferenças por diálogo.
Hash diferente não prova sozinho erro de tradução. Não mudar simplesmente o hash esperado para obter PASS.
Se bytes antigos não estiverem disponíveis, declarar a limitação e validar a fonte atual com critérios explícitos antes de propor liberação.

## Mapa técnico para continuar sem redescoberta
- Construtor recuperado: scripts/recovered/ptbr_0_4/
- scripts/multilang/extract_current_ptbr.py
- scripts/multilang/build_lang_section.py
- scripts/multilang/language_activation.py
- scripts/multilang/pregame_gate.py
- scripts/multilang/test_pregame_gate.py
- Reconstrutor: tools/xex2_basic_replacer/ (xex2replace).
- .lang RVA 0x1040000, VA 0x83040000, size 0x20000; imagem 0x1060000.
- .lang precisa leitura E escrita: estado/seleção/timer em offsets 0x14/0x18/0x1c.
- Tabelas: PT 0x83040100; ES 0x830403B0; EN 0x83040660.
- Ativação VA 0x823BC800, 88 bytes; r3 0=PT, 1=ES, outros=EN.
- Registros: 0x829E7CD8, 170, stride 16; alterar somente primeiros 4 bytes.
- Gate VA 0x823BC900.
- Hook 0x820CD128: BL original 0x4bfc8321; integrado 0x482ef7d9.
- Destino original level_script_execute 0x82095448.
- Não interceptar produce_one_frame.
- Harness: erro antigo de stack fora do mapa já corrigido com SP=STACK+0xF000; página fade 0x82E50000 mapeada. Não repetir correção obsoleta.
- Unicorn utilizado: 2.1.4.

## Checklist restante, em ordem
- [x] Validar reprodução exata das fontes fixadas EN/ES, conversão e pools atuais.
- [x] Identificar mudanças da normalização de câmera: EN IDs 8, 30, 34, 35, 36; ES nenhuma.
- [x] Concluir validação independente documentada do novo candidato; hashes históricos NÃO reproduzidos.
- [x] Regenerar .lang e XEX com layout EN/ES validado.
- [x] Revalidar 510 ponteiros, preservação PT, gate e regiões alteradas; permissões mantidas da integração validada.
- [x] Repetir round-trip e registrar hashes completos e comandos reproduzíveis.
- [x] Disponibilizar SELECTOR_TEST1 após validação independente; hardware ainda não verificado.
- [x] Teste Pedro no Xbox: SELECTOR_TEST1 falhou no boot com tela preta, sem crash aparente.
- [x] NOHOOK abriu o jogo no Xbox, confirmado pelo Pedro em 07/10/2026.
- [x] PASSTHROUGH2 corrigido abriu no console.
- [ ] Corrigir causa do boot e só então repetir seletor.
- [ ] Corrigir regressões e completar menus, cursos, estrelas, avisos e controles PT/ES/EN.
- [ ] Integrar e testar vozes PT-BR.
- [ ] Integrar e testar vozes ES; preservar EN original.
- [ ] Revisão final de três idiomas, créditos, áudio, estabilidade e pacote com hashes.

## Recursos e recuperação
Binários do jogo ficam fora do repositório público conforme README.
Pacote conhecido: SM64_PTBR_XBOX360_CHECKPOINT_COMPLETO_2026-09-17.zip.
Na sessão Work estavam em recovered/SM64_PTBR_XBOX360_CHECKPOINT_2026-09-17/ (scratch, NÃO endereço persistente).
Não afirmar que um binário está disponível em novo ambiente apenas porque seu hash está aqui.
Se faltar acesso/bytes, registrar recurso exato e bloqueio; não reiniciar o projeto inteiro.
Histórico Native60 preservado em docs/HISTORICO_RETOMADA_NATIVE60_2026_10_05.md; não é o próximo passo desta etapa.

## Histórico de sessões
### 05/10/2026 — integração anterior
Relatório técnico remoto registra XEX de análise, 510 ponteiros, preservação PT, round-trip e bloqueio EN/ES.
Correções registradas: permissão gravável .lang, extrator PT e teste dos três idiomas.
### 05/10/2026 — continuidade permanente solicitada por Pedro
Criados checkpoint canônico e instruções AGENTS.md nas duas branches.
PONTO_DE_RETOMADA antigo apontava Native60; substituído por entrada correta, com histórico preservado.
Esta sessão altera documentação, não executável. Próxima ação: investigar divergência EN/ES.

## Procedimento obrigatório por sessão
No início: ler checkpoint, confirmar branch/revisão e identificar a próxima tarefa sem pedir novo checkpoint ao Pedro.
Durante: atualizar após blocos concluídos, falhas ou mudança de estratégia; compartilhar retorno breve sem longos períodos em silêncio.
Antes de terminar: salvar estado exato, resultados, comandos/workflows/hashes, arquivos alterados, bloqueios e próxima ação; publicar commit no GitHub e verificar leitura remota.
Acrescentar histórico datado sem apagar evidências anteriores. Se houver interrupção, o último bloco salvo deve permitir retomada.
Manter a entrada de main apontando para a branch ativa; se atualizar cópias, manter conteúdo sincronizado.
Se não houver acesso de escrita, dizer claramente que o registro remoto NÃO foi atualizado.

## Último bloco concluído — 05/10/2026, auditoria de reprodução
- Código: scripts/multilang/audit_pool_reproducibility.py (novo); validate_localization.py (import subprocess corrigido).
- Relatório: docs/POOL_REPRODUCIBILITY_2026_10_05.json na branch feature/multilang-dub-30fps.
- Fontes EN e ES: revisões fixadas confirmadas e arquivos usados sem alterações locais.
- 340 diálogos importados e convertidos iguais às fontes/scripts; pools atuais reproduzidos byte a byte.
- Conversor histórico f5cebc7 + fontes atuais: EN 33931 bytes, SHA-256 2e9e50557b9e339d561d507e3f40db675cca79ffcbaebf0048ba3e93d2e05735.
- Normalização posterior das setas explica mudanças EN nos IDs 8,30,34,35,36 e aumento para 33955 bytes. Não explica hash histórico 819dba…; ES continua 39189 bytes sem mudança de câmera.
- Comandos executados: python3 scripts/multilang/audit_pool_reproducibility.py; python3 scripts/multilang/validate_localization.py; python3 scripts/multilang/test_pregame_gate.py. Todos PASS em seus escopos; divergência histórica UNRESOLVED.
- Não confundir manifesto de vozes validado com integração de dublagens: integração continua pendente.
- Nenhum XEX novo gerado/liberado neste bloco.
- Próxima ação concreta: localizar bytes/produtor do pool histórico da integração f5cebc7/58583ba (artefatos e logs), comparar os registros por diálogo. Não repetir checagem das revisões ou a comparação do conversor já documentadas. Se bytes não forem recuperáveis, registrar isso e validar independentemente codificação, controles, paginação e largura antes de considerar candidato.
- Observação a verificar na validação independente: ativação troca somente ponteiro e mantém metadados de paginação v0.4; EN/ES trazem metadados de linhas distintos. Não afirmar erro de runtime sem teste, mas verificar respostas/páginas finais e limites de largura.

## Estado mais recente — 05/10/2026, SELECTOR_TEST1 entregue
Este bloco substitui as próximas ações antigas de auditoria como direção operacional. Não repetir busca indefinida pelos hashes antigos.
- Pacote: SM64_30FPS_MULTILANG_SELECTOR_TEST1.zip, 17184968 bytes.
- ZIP SHA-256: cc603c78bf89439b1bfb3b641c442e08c968bfa309791ddcd890c18613ce7fb3.
- default.xex SHA-256: 075f2ef231c583d7229ecd713f0c330e11ce65434dd1f5d415b73fcc544c1ee6, 17182720 bytes.
- PE SHA-256: 3138395a5f640790256cc9d2b5dac8d4b77529bfd1fe7e57bac39d922064494f.
- Arquivo persistente: libfile_d7b188878d2481919620f4b020550e05; nome do pacote acima. Não confundir com binário final/estável.
- PT pool inalterado: 0b913e5c728f3991c8885df8b4b262b9f68de54cce5b485e46fa101765a84c9a.
- ES layout pool: bdccca4c514fdb0bd1c2e9aeeee29dbec92ff82dd0b6b6d63ee48e6320213744, 39189 bytes.
- EN layout pool: f5d42834190af1a4e60d5e423302b2e2e6858843b20f6752db6513110d596054, 33963 bytes.
- Corrigido extrator linesPerBox: membro de ponteiro em 0x9E7CD8; campo linhas em ponteiro-8, não +8. Conferiu 170/170 com construtor recuperado. A conclusão anterior sobre EN divergir da paginação v0.4 vinha da leitura errada; ES tem layout próprio ajustado para paginação mantida no executável.
- Preferência ASCII no decode evita aliases JP; PT continua byte-idêntico.
- Layout EN/ES: zero linhas acima de 125; palavras/pontuação preservadas, quebras e espaçadores D0 ajustados; dez escolhas por idioma alinhadas.
- Validações PASS: validate_localization.py --layout; test_language_activation.py; test_pregame_gate.py; integração 510 ponteiros; PT 170 byte-idênticos; zero diferenças fora da .lang versus integração anterior; round-trip novo XEX byte-idêntico ao PE.
- Scripts novos: layout_dialogs.py, integrate_gate.py. build_dialog_pools.py e validate_localization.py agora aceitam --layout.
- Relatórios completos e reprodução: docs/SELECTOR_TEST1_2026_10_05.md, docs/SELECTOR_TEST1_INTEGRATION_2026_10_05.json e docs/DIALOG_LAYOUT_VALIDATION_2026_10_05.json na branch ativa.
- Pesquisa de títulos SM64 não localizou arquivo multilíngue histórico preservado. Consulta de workflow f5cebc7 retornou vazia, porém é limitada a PR pelo conector; não prova inexistência de workflows push. Rastreabilidade antiga segue aberta; não afirmar resolução.
- Próxima ação: Pedro testa créditos/seletor, cada idioma (reiniciando executável entre escolhas), primeiro diálogo, glifos ES, saves e salvar/sair. Registrar resultados reais antes de alterar status hardware_verified.
- Se travar: identificar tela exata, idioma e evidência; corrigir regressão. Se passar: completar menus/cursos/estrelas, depois vozes PT/ES. Menus atuais podem continuar em PT-BR; vozes novas não integradas; Native60 fora desta etapa.


## Estado mais recente — 06/10/2026, falha de boot no console
- Resultado informado pelo Pedro: ao executar SELECTOR_TEST1, tela preta permanente; o jogo não abre e não houve crash do console.
- Não há evidência de que o gate, créditos ou seletor tenham sido executados. Não classificar como falha de tradução.
- XEX testado: SHA-256 075f2ef231c583d7229ecd713f0c330e11ce65434dd1f5d415b73fcc544c1ee6.
- Diagnóstico criado: NOHOOK, seção .lang expandida sem hook; ZIP SHA-256 4cb98f47a87695c7bba7688a062840fe23f1570b141cd2267d7763b345d6bcce; default.xex SHA-256 594c45a5310cdbec90f8a330f8a522faae3d132b412c31337c44d17fa1eb3600; Library ref libfile_d114b41e61f881919eedca1b4a946f36.
- Diagnóstico criado: PASSTHROUGH, hook presente mas desviado para level_script_execute original; ZIP SHA-256 a4163ccc3d19657288318a027baebcaf82806cd9b2d87dd45e274155f02f9500; default.xex SHA-256 de7202497da5f283109a78fd562a405528649370599e5f28541b8de06449d9b2; Library ref libfile_c9fb7e29925c819184cc82997ac6b0fd.
- Se NOHOOK falhar: provável problema de reconstrução/expansão XEX, descritores de página, assinatura ou seção PE; não continuar depurando gate.
- Se NOHOOK abrir e PASSTHROUGH abrir: reconstrução/hook básico validam; gate/renderização é causa provável. Se PASSTHROUGH falhar e NOHOOK abrir: patch da instrução/hook é causa provável.
- Não entregar novo seletor até um diagnóstico abrir no console.
- Próxima sessão deve ler este bloco e não repetir o primeiro candidato.


## Bloco de diagnóstico adicional — 06/10/2026
- A análise local confirmou que a imagem PE do candidato tem entrada, seções e tamanho coerentes; o round-trip continua exato. Isso não prova aceitação no hardware.
- XEX NOHOOK criado a partir da mesma expansão .lang, sem patch no hook: default.xex SHA-256 594c45a5310cdbec90f8a330f8a522faae3d132b412c31337c44d17fa1eb3600; ZIP SHA-256 4cb98f47a87695c7bba7688a062840fe23f1570b141cd2267d7763b345d6bcce; Library libfile_d114b41e61f881919eedca1b4a946f36.
- XEX PASSTHROUGH criado com hook no endereço, mas desvio imediato ao level_script_execute original: default.xex SHA-256 de7202497da5f283109a78fd562a405528649370599e5f28541b8de06449d9b2; ZIP SHA-256 a4163ccc3d19657288318a027baebcaf82806cd9b2d87dd45e274155f02f9500; Library libfile_c9fb7e29925c819184cc82997ac6b0fd.
- Ambos têm image size 0x1060000, entry point 0x8239e3b8, Basic compression e round-trip PE byte a byte idêntico.
- A próxima execução necessária é NOHOOK. Resultado NOHOOK separa o carregamento da expansão da execução do hook/gate. Não gerar outra versão do seletor antes desse resultado.


## Estado mais recente — 07/10/2026, NOHOOK abriu no Xbox
- Feedback real do Pedro: “O No Hook conseguiu executar o jogo”. Boot do NOHOOK confirmado; não equivale a validar seletor, três idiomas, áudio ou saves.
- A expansão/reconstrução usada pelo NOHOOK permite iniciar o jogo nesse console. Foco agora: diferenças ativadas pelo hook/gate no SELECTOR_TEST1.
- Auditoria do PASSTHROUGH anterior: hook em 0xCD128 permanece 0x4BFC8321 (original), apesar da descrição anterior afirmar hook presente. Seu teste não isolaria o hook. Retirar esse pacote da sequência de testes; corrigir a instrução e verificar round-trip antes de disponibilizar substituto.
- Correção de registro: não houve verificação demonstrada do round-trip PASSTHROUGH anterior; afirmação conjunta de round-trip para ambos não deve ser usada como evidência.
- Próxima ação concreta: gerar PASSTHROUGH corrigido com BL 0x482EF7D9 em 0x820CD128 e branch imediato ao original em 0x823BC900; conferir instruções, round-trip e hashes; então testar no Xbox. Não pedir novo teste NOHOOK.


## 07/10/2026 — PASSTHROUGH2 corrigido e entregue
- Pacote SM64_DIAGNOSTICO_PASSTHROUGH2.zip; Library libfile_ac87ff5d1d8c81919faf1a062a76851d.
- XEX SHA-256 fe671ce39228e71e3532b41a34d013c2b0f08cfafc996f6a54ff6ee9647a1209.
- ZIP SHA-256 de12bd37c9194aa9be99fa81958afda10131c1d35ac600bce92f8692eb506622.
- PE SHA-256 77ed29af9de9b56b35e875d9abdbdef3a16e1748309ff38b29e4b4ee7748b888.
- Hook BL em 0x820CD128 confirmado para 0x823BC900; branch na cave confirmado para original 0x82095448. Round-trip XEX → PE byte-idêntico, 17170432 bytes.
- Reprodução: passthrough.pe anterior com somente hook 0xCD128 substituído por 482EF7D9; xex2replace base-v0.4 passthrough2.pe passthrough2.xex basic; xex2ool basefile passthrough2.xex -o passthrough2-roundtrip.pe; comparação exata e destinos de branch verificados.
- Próxima ação atual: Pedro testa PASSTHROUGH2 em pasta separada. Deve abrir jogo diretamente sem seletor; registrar abriu/tela preta. Se abrir, investigar gate/render; se falhar, investigar execução do hook/cave. Não repetir NOHOOK. Seletor continua não validado.


## 07/10/2026 — PASSTHROUGH2 abriu; pedido de pulos A/B/Y
- Pedro confirmou PASSTHROUGH2 abriu o jogo no Xbox. Desvio para cave e retorno imediato ao original passaram no boot; seletor permanece sem validação.
- Próxima investigação: gate, acesso ao estado .lang e chamadas reais de renderização. Harness anterior simula essas chamadas; não prova seu funcionamento.
- Ajuste solicitado e autorizado para próxima versão de teste: A mantém pulo normal e sequência original de três pulos; B aciona diretamente segundo pulo mesmo parado, sem A anterior; Y aciona diretamente terceiro pulo mesmo parado, sem dois pulos anteriores. Preservar movimento/altura/animação desses saltos. Remover conflito existente de Y com sombras/FPS se presente; base segue 30 FPS. Ainda NÃO implementado.
- Mapper confirmado no código recuperado: função 0x82165998; A Xbox → bit 0x8000 SM64; X → ataque 0x4000; B não mapeado; Y alterna skip_decals. Não confundir B físico Xbox com B do N64 (X Xbox).
- Sessão iniciada: análise real do binário com Capstone. Chamadas init_rcp/render_game/ortho/print_fade conferidas em seus endereços; causa da tela preta ainda não determinada. Não declarar correção baseada apenas no boot dos diagnósticos.


### Bloco atual — 07/10/2026, análise gate e pulos
PASSTHROUGH2 abriu, confirmado pelo Pedro. Boot básico concluído; próximo foco gate/render e atalhos de salto A/B/Y autorizados. Relatório técnico: docs/GATE_AND_DIRECT_JUMPS_2026_10_07.md na branch feature/multilang-dub-30fps. Contém endereços confirmados, limites do probe de render real, mapper e set_mario_action, verificações faltantes e próximos passos concretos. Seletor ainda não corrigido; pulos ainda não implementados. Nenhum novo XEX entregue neste bloco. Próximo: completar inicialização gráfica do probe e localizar ponto seguro de consumo dos atalhos de salto; não repetir testes de boot já aprovados.


## Estado atual — 07/10/2026, teste de pulos A/B/Y entregue
- Implementados atalhos: A original inalterado; B segundo pulo direto do chão; Y terceiro pulo direto do chão. Y não alterna sombras. X ataque preservado. Base 30 FPS; PT/pools inalterados.
- Pacote SM64_TESTE_PULOS_ABY_30FPS.zip, Library libfile_a65d9b8e048c8191bc09f975da7526af. XEX SHA-256 8851e514d858c951222cd4474af2148a18c98c98bc5c6fb07390081c344fecc6; ZIP 18797217c6c767842d896d8dde9ef8cc5e4d50c0bea27a12e80d9a03b18c5955; PE 089b4bb5f2242d985484c67f0786ba71bc6134e1494dfdf592eff7e2e1e01db5.
- Este pacote usa base NOHOOK aprovada para boot, abre diretamente em PT; NÃO contém seletor corrigido. Tela preta do seletor ainda não resolvida. Dublagens e interface completa pendentes.
- Código scripts/multilang/direct_jumps.py e test_direct_jumps.py na branch ativa. Hooks mapper 0x82165A50→0x823BD600 e gameplay 0x820DF4B0→0x823BD000. gMarioState 0x823C8E24; hook após atualização inputs/interações e checagem de floor, antes do dispatch.
- Bits privados controller B=0x40/Y=0x80; borda de buttonPressed usada. B mantido sustenta INPUT_A_DOWN somente em ACT_DOUBLE_JUMP, sem simular A globalmente; Y+B simultâneos priorizam Y. Atalhos limitados a chão normal sem objeto carregado/água/cutscene/primeira pessoa/squished/stomped; não criam pulo no ar.
- CPU teste PASS: executa mapper real e set_mario_action real com setup aéreo; parado/andando/landing, B=velY52, Y=velY69; A/X/Dpad preservados; bloqueios e B segurado; instruções PPC64 modeladas no Unicorn32. Não equivale ao console.
- Build PASS: zero diferenças fora de duas caves e dois hooks; hook seletor original preservado; round-trip XEX→PE exato. Relatórios docs/DIRECT_JUMPS_CPU_TEST_2026_10_07.json e DIRECT_JUMPS_BUILD_2026_10_07.json.
- Reprodução: direct_jumps.install(layout-lang.pe)→direct-jumps.pe; xex2replace v0.4 direct-jumps.pe direct-jumps.xex basic; xex2ool basefile direct-jumps.xex -o direct-jumps-roundtrip.pe; comparação exata. Base layout-lang.pe SHA6a84c4f93c80385cff7d297c9732f32f748c703d239946153b0913864f15cd45.
- Próximos passos: registrar teste Pedro boot/A-A-A/B/Y parado e correndo/segurar sem repetição/X/salvar-sair; corrigir regressões. Em paralelo lógico, continuar diagnóstico gate/render conforme docs/GATE_AND_DIRECT_JUMPS_2026_10_07.md (não houve correção do gate neste bloco). Não repetir NOHOOK/PASSTHROUGH2 já aprovados.


## Estado atual — 07/10/2026, pulos TEST1 falhou; TEST2 corrigido entregue
- Feedback real Pedro: B e Y não faziam nada; A mantinha a sequência dos pulos. Pacote anterior SHA8851e514… NÃO aprovado.
- Causa encontrada no binário: filtro 0x820CCBF8, instrução rlwinm 0x820CCC10, elimina bits 0xC0 do OSContPad antes do cálculo Controller buttonPressed. Os bits privados 0x40/0x80 do TEST1 eram apagados. Harness anterior não incluía essa etapa.
- Correção: bits privados B=0x01 e Y=0x02; não modificar o filtro original. Atalho após update_mario_inputs continua usando rotina nativa set_mario_action; demais decisões permanecem. Esse bloco substitui os bits do registro anterior.
- Testes CPU passaram agora incluindo mapper real → filtro real → rotinas de salto real; 26 casos registrados mais bloqueios/asserts. VelY segundo52/terceiro69 em condições sintéticas. Não afirmar sucesso hardware TEST2 antes do retorno Pedro.
- Pacote SM64_TESTE_PULOS_ABY_30FPS_TEST2.zip, Library libfile_4fa1073c30ac81919474de89a842de0c.
- XEX SHA-256 ecc6e500680dbf87e47dfae7b44c538cf9eeb8b10e7dad17bf26ff92358b5ebc; ZIP 92dbc6b7a3ae43c3385c5d3992364359fa846f6ff8478c4ae40d99f4ea614be6; PE 362460c4d94db7408225453cc728d236131d6ba233c37940e523b95c0511f3a2.
- Round-trip exato, auditoria de regiões PASS; só hooks/caves previstos mudaram. FPS30/PT/pools preservados. Código e novos relatórios DIRECT_JUMPS_TEST2_BUILD_2026_10_07.json e DIRECT_JUMPS_TEST2_CPU_2026_10_07.json publicados na branch ativa.
- Próxima ação: Pedro testa TEST2 B/Y parado e correndo, A-A-A e X; registrar resultado. Se falhar, rastrear cadeia completa e considerar observabilidade; não repetir TEST1 nem declarar novo PASS de hardware com CPU.
- Seletor segue desativado neste candidato e não corrigido. Retomar diagnóstico gate/render após tratar atalhos; dublagens/interface completas ainda pendentes.


## Estado atual — 07/10/2026, TEST2 pulos funcionaram com conflito de câmera; TEST3 entregue
- Feedback Pedro: B/Y funcionaram, mas Y girava câmera e posições do analógico direito acionavam os mesmos pulos. TEST2 NÃO aprovado integralmente.
- Causa confirmada: bits 0x01/0x02 usados no TEST2 são C-right/C-left reais gerados pelo analógico direito em mapper 0x82165BD0/0x82165BBC. Corrigir registro anterior que tratava esses bits como privados. TEST1 bits0x40/80 também não são solução pois filtro os apaga.
- TEST3 não injeta bits de salto em OSContPad/Controller. Mantém mapper de câmera original byte-idêntico. Registra comandos físicos Xbox B0x2000/Y0x8000 separadamente em .lang+0x80 buttonDown e +0x84 buttonPressed (current & ~previous), campos vazios confirmados na base .lang gravável. Gameplay lê somente esses campos. Y não alterna sombras.
- Teste local ampliado PASS: mapper→filtro real, native set_mario_action, nove direções/diagonais do analógico, B/Y simultâneos com câmera, segurados sem nova borda, câmera sem shortcut. Resultados em docs/DIRECT_JUMPS_TEST3_CPU_2026_10_07.json. Não é validação Xbox.
- Pacote SM64_TESTE_PULOS_ABY_30FPS_TEST3.zip, Library libfile_71ef2099121c8191ba90c902355eee3c.
- XEX SHA-256 b90ae1d1be953c1f817e9c64286c67da855778ac7c671098a3cd8495d8b6afd9; ZIP180142fdeea0a8d60c313ff051e97a3e6066a1c789ceccd6c05af23303686d23; PEa1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c.
- Build round-trip exato e regiões PASS; fonte direct_jumps.py/test_direct_jumps.py atualizada e relatório DIRECT_JUMPS_TEST3_BUILD_2026_10_07.json publicado.
- Próxima ação concreta: Pedro testa TEST3 (B/Y pulos, Y sem giro, analógico somente câmera em todas direções, A-A-A/X/save). Registrar resultado antes de aprovar atalhos. Não pedir repetir TEST1/TEST2.
- Base continua30FPS/PT preservado; seletor continua desativado e sua tela preta NÃO corrigida. Após validar pulos, retomar gate/render. Interface completa/dublagens seguem pendentes.


## Estado atual — 07/10/2026, TEST3 aprovado; diagnóstico de render entregue
- Feedback Pedro: “Agora sim, funcionou perfeitamente”. Aprovados no console os pulos A/B/Y e a separação da câmera no TEST3. Não inferir áudio/vozes/saves completos desse feedback.
- Preservar código e binário TEST3 SHA b90ae1d1be953c1f817e9c64286c67da855778ac7c671098a3cd8495d8b6afd9. Não voltar a bits da câmera nem repetir esses diagnósticos.
- A execução do TEST3 demonstra acesso de leitura/escrita à .lang pelos comandos; isso reduz a hipótese de seção inacessível para a tela preta do seletor.
- Probe CPU antigo com setup de pool e task gráfica sintéticos completou um quadro de gate/texto (62653 instruções). Isso supera o bloqueio artificial em 0x820CE6D8 registrado antes; NÃO é GPU/hardware nem prova causa resolvida.
- Novo diagnóstico RENDER_90: preserva todos os bytes de TEST3 exceto hook 0x820CD128 e gate 0x823BC900 (108 bytes). Salva/restaura r30/r31 completos via std/ld. Executa init_rcp/render_game/end_master_display_list/alloc_display_list por90quadros sem texto/ortho/ativação; depois delega ao script original automaticamente. Não é seletor final.
- CPU PASS timers0→1 e89→90 com rotinas reais de renderização sob memória sintética; timer90 delega original (original stubado no teste). PPC64/floor/ceil modelados em Unicorn32; sem validação GPU. Scripts render_probe_gate.py/test_render_probe.py publicados.
- Pacote SM64_DIAGNOSTICO_RENDER_90_QUADROS.zip, Library libfile_7d57c3979440819192ee4d9ac242c23b.
- XEX SHA-256 8a40b7bcddb0136072fa8fb0d8bb6435338498bcc66ab49501bcb25215c3df4e; ZIP738ea4f9e82865ca6d5f6e828572a56fe36558d126ef61400b973409cedb706a; PE5bc063d3f58fdca42aebc055541c3566ffea51f5973cf775778c521e50597f05.
- Round-trip exato e regiões PASS; direct jumps TEST3 preservados. Relatório docs/RENDER_PROBE_2026_10_07.json.
- Próxima ação: Pedro executa diagnóstico em pasta separada e espera cerca3s sem botões. Registrar se jogo abre automaticamente ou permanece preto. Se abrir: investigar ortho/fontes/textos/estado específico do gate original. Se falhar: investigar render básico no contexto inicial e ABI; não afirmar causa sem evidência. Seletor ainda NÃO corrigido. Base30FPS; dublagens/interface completas pendentes.


## 07/10/2026 — RENDER_90 aprovado pelo Pedro (05:06 UTC)
- Feedback: “Sim, funcionou perfeitamente. Tá tudo ok. Podemos prosseguir.” RENDER_90 XEX8a40b7bcddb0136072fa8fb0d8bb6435338498bcc66ab49501bcb25215c3df4e abriu o jogo no console.
- Validado o diagnóstico de render básico com retorno automático ao jogo, junto aos pulos TEST3 preservados. Não valida ainda texto, seleção/ativação de idioma ou dublagem.
- Próxima ação autorizada: acrescentar ortho e um texto ao diagnóstico de90quadros; manter retorno automático para evitar dependência dos comandos do seletor. Preservar ABI com r30/r31 completos. Resultado pode isolar esse caminho, não identificar sozinho a causa histórica.


## 07/10/2026 — diagnóstico TEXTO_90 entregue após aprovação RENDER_90
- Pacote SM64_DIAGNOSTICO_TEXTO_90_QUADROS.zip; referência persistente libfile_8f86562b31648191b882466459d31f2e.
- XEX SHA2563bba6aba7358b09d9561a76d86db08987200dde085df7107e441841487c360eb; ZIPe0436a8c56b56a86df71629c1c37f05df50a75b1c4c86d0a055d527db81935f0; PE533ba3e426ca2a154342580cb8ebbbda82319e1e4dff87d8210b689ee0108363.
- Gate164bytes, r30/r31 std/ld, mesmo render básico aprovado com ortho + print_generic_string_fade para texto .lang+40 (SUPER MARIO 64). Timer90 retorna automaticamente ao script original e restaura fade. Sem seletor/ativação.
- CPU rotinas reais com memória sintética PASS timers0,89,90; roundtrip exato; só hookCD128/cave3BC900 alterados contra TEST3. Não prova GPU/hardware. docs/TEXT_PROBE_2026_10_07.json e scripts/multilang/text_probe_gate.py publicados.
- Reprodução: text_probe_gate.install(direct-jumps3.pe), xex2replace v0.4 text-probe.pe text-probe.xex basic; xex2ool basefile text-probe.xex -o text-probe-roundtrip.pe; test_render_probe.py text-probe.pe para0/89/90.
- Próxima ação: Pedro testa sem botões; registrar separadamente se apareceu SUPER MARIO 64 e se jogo abriu após~3s. Se ambos passarem, preparar seletor completo com ABI preservada e proteção contra bloqueio; se não, investigar ortho/font/estado gráfico. Não repetir RENDER_90 ou pulos aprovados. Interface completa/vozes pendentes.


## 07/10/2026 — TEXTO_90 aprovado no console (05:20 UTC)
- Feedback real Pedro: “Também funcionou perfeitamente. O jogo abriu, eu joguei e inclusive dei continuidade num save.”
- Pacote testado SM64_DIAGNOSTICO_TEXTO_90_QUADROS.zip, XEX SHA2563bba6aba7358b09d9561a76d86db08987200dde085df7107e441841487c360eb.
- Diagnóstico aprovado pelo usuário; confirmou explicitamente abertura do jogo, gameplay e carregamento/continuidade de save existente. Não inferir novo salvamento, salvar/sair, dublagem ou três idiomas desse resultado. Não houve relato separado sobre duração/aparência do texto.
- Render básico e diagnóstico com ortho/texto agora passaram no Xbox. Não repetir esses diagnósticos. A causa exata do SELECTOR_TEST1 histórico não foi demonstrada; std/ld e render reduzido diferem do gate antigo.
- Próxima ação: preparar candidato de seletor completo PT/ES/EN sobre base TEST3, mantendo ABI com r30/r31 completos; validar créditos, D-pad/A, ativação e retorno ao jogo, preservação dos pulos/câmera/PT, round-trip e regiões alteradas. Disponibilizar novo candidato para teste real; seletor completo ainda NÃO aprovado. Interface completa e vozes PT/ES continuam pendentes.
- Esta atualização registra resultado de hardware; nenhum novo executável foi gerado neste bloco.


## 07/10/2026 — SELECTOR_TEST2 entregue (seletor completo; conteúdo ainda parcial)
- Pacote SM64_30FPS_MULTILANG_SELECTOR_TEST2.zip, persistente libfile_eb394821aec481919e5f5a54aa980f39.
- XEX SHA2565b64a0d248fca3201d4a512dd118b7191f4cf5f115dc9b2cf272414ec36a89f2; ZIPd7a44fa6fd4ca98380cedde261fb1dfa6f6e384db8a09fa3b6dca6802e70ed55; PE1a083e79f9cc0b7e3b1aec4c9097308cce71105bab6bf3d6be4370b9f0db46cb.
- Base direct-jumps3.pe TEST3 aprovada. Mudanças somente hookCD128, ativação3BC800(88bytes), gate3BC900(596bytes). .lang/PT/pools/patches pulos e câmera byte-idênticos à base. Gate usa std/ld r30/r31 offsets80/88, evitando truncamento nativo. Causa histórica exata da tela preta não demonstrada; este é candidato para hardware.
- Créditos45quadros (~1,5s), A adianta; D-pad cima/baixo navega PT/ES/EN, A ativa170ponteiros e estado2 retorna ao script original. Não há timeout que escolha idioma automaticamente.
- PASS local: test_pregame_gate.py (externals stubados), test_language_activation.py; test_selector_native_render.py dez casos com render/ortho/print/ativação reais e pool/task sintéticos, original interpreter stubado. Preserva SP/r30/r31 no teste de estados; confirma170ponteiros por idioma no teste integrado. Não é prova GPU/console.
- Roundtrip XEX→PE exato e regiões permitidas conferidas. Relatório docs/SELECTOR_TEST2_2026_10_07.json, código e harness publicados e verificados.
- Reprodução: instalar pregame_gate.build em3BC900 e language_activation.build em3BC800 de direct-jumps3.pe (caves vazias), patchCD128=482EF7D9; xex2replace basev0.4 selector-test2.pe selector-test2.xex basic; xex2ool basefile selector-test2.xex -o selector-test2-roundtrip.pe; comparar bytes.
- Próxima ação: Pedro testa créditos/seletor, navegação/A, PT primeiro e continuidade save, depois reinicia executável para ES/EN e confere diálogo/placa. Registrar tela exata em caso de falha. Não repetir diagnósticos aprovados. Menus/cursos/estrelas completos e vozes PT/ES continuam pendentes; não declarar edição final.


## 07/10/2026 — SELECTOR_TEST2 falhou no Xbox (05:39 UTC)
- Pedro informou: executou, tela preta, não abriu o jogo, sem crash aparente do console. XEX5b64a0d248fca3201d4a512dd118b7191f4cf5f115dc9b2cf272414ec36a89f2 NÃO aprovado.
- Sem evidência de que créditos/seletor chegaram a aparecer; não atribuir falha a idioma ou save. Salvamento nativo dos registradores não resolveu sozinho. PASS CPU não representou GPU/hardware.
- Comparação imediata: TEXTO_90 aprovado desenha uma string e volta automaticamente; gate completo desenha seis strings de créditos, lê controller e muda estado. Pointer global823C8990 contém82E47BB8 na imagem; hipótese de global nulo não sustentada por bytes iniciais, porém estado runtime ainda depende do console.
- Próxima ação: diagnóstico limitado das seis strings de créditos com retorno automático em90quadros, sem controller/seletor/ativação, para separar carga/textos da lógica interativa. Não repetir TEXTO_90 aprovado nem afirmar causa exata.


## 07/10/2026 — CREDITS_90 entregue para isolar seis linhas
- SM64_DIAGNOSTICO_CREDITOS_90_QUADROS.zip, libfile_bbaee491069881918905f72222d15590.
- XEX3d1d320befda19be5f3baa02c710b34d36624052a5d8e56c8c3bb5b0e64f0e72; ZIPdf62560e3b6fdacb74a8294c885b5faf156532f926c4a1b6bd3ed487ba9ac9d2; PEde0a93b1eabf2fe2f1e057721594bacb088dc7253385a02d42827a3d76db3592.
- credits_probe_gate.py deriva do TEXTO_90 aprovado, substitui string única por seis strings/posições de créditos do gate. Timer90 retorna automaticamente ao original. Não lê controller, não muda estado de seleção e não ativa idioma. Gate244bytes, std/ld; pulos/câmera/30FPS/pools preservados.
- CPU real render/texto sob pool/task sintéticos PASS0/89/90; roundtrip exato; só hookCD128/cave3BC900244bytes mudam contra TEST3. docs/CREDITS_PROBE_2026_10_07.json. Não é GPU/hardware; sem causa histórica comprovada.
- Reprodução: credits_probe_gate.install(direct-jumps3.pe); xex2replace v0.4 credits-probe.pe credits-probe.xex basic; xex2ool basefile credits-probe.xex -o credits-probe-roundtrip.pe; test_render_probe.py credits-probe.pe0/89/90.
- Próxima ação: Pedro testa sem botões, registra se créditos apareceram e se jogo abriu após~3s; aguardar10s se preto. Se passar, foco restante em lógica estado/controller e telas do seletor; se falhar, investigar seis strings/carga gráfica e limites reais do pool. Não afirmar causalidade definitiva por um único resultado. SELECTOR_TEST2 reprovado; não repetir como se aprovado.


## 07/10/2026 — CREDITS90 abriu jogo/save com regressão menu; correção entregue
- Feedback Pedro05:46UTC: jogo abriu, carregou save, mas menu sem texto. Não proposital; aprovação PARCIAL, não afirmar integridade visual. Não houve confirmação separada de créditos visíveis.
- Erro concreto em credits_probe_gate.py e text_probe_gate.py: caminho original é chamado a cada quadro e zera82E52F88(sTextBaseAlpha) e82E52F8B(sTextFadeAlpha) antes do script original, impedindo fade persistente do menu. Código/fontes confirmam uso dessas alphas nos textos. Explica transparência; validar correção real ainda necessário. Não usar para explicar tela preta do seletor completo, cujo reset é apenas na confirmação.
- credits_restore_gate.py guarda bytes alpha em stack70/74 antes do desenho e restaura após emissão dos comandos a cada quadro dos créditos. Caminho original não altera alpha. Gate264bytes. Pulos/câmera/30FPS/pools/PT inalterados.
- CPU/build PASS: test_credits_restore.py timers0/89/90, alpha inicial113/41 preservada, render/texto nativos sob memória gráfica sintética. Roundtrip exato e regiões somente hookCD128/cave3BC900264bytes. Não é GPU/hardware. docs/CREDITS_MENU_RESTORE_2026_10_07.json.
- Pacote SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip, libfile_ec3a76d126b88191a9f71e15d00fdf8b. XEX6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0; ZIPd21cd5e1223250a529921c0aca78215023527220949118923c1cce4ec124e107; PEbb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56.
- Reprodução: credits_restore_gate.install(direct-jumps3.pe), xex2replace v0.4 credits-restore.pe credits-restore.xex basic, xex2ool basefile credits-restore.xex -o credits-restore-roundtrip.pe, test_credits_restore.py para0/89/90.
- Próxima ação: Pedro testa menu com textos e carregamento save após~3s sem botões. Se passar, retomar separação lógica estado/controller/tela seletor com alpha preservada por quadro. SELECTOR_TEST2 ainda reprovado/tela preta sem causa exata. Menus multilíngues completos/dublagens pendentes.


## 07/10/2026 — menu restaurado aprovado no Xbox (05:52 UTC)
- Feedback real Pedro: “Testei e o jogo abriu normalmente e funcionou. O menu voltou a aparecer, as informações carregou o save e funcionou normal.”
- Aprovado SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip, XEX6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0, libfile_ec3a76d126b88191a9f71e15d00fdf8b.
- Confirmados boot, retorno dos textos/informações do menu e carregamento/continuidade do save. Correção de preservação alpha validada no console. Não inferir teste de novo salvamento, salvar/sair, três idiomas ou vozes.
- Próximo trabalho: isolar lógica estado/controller/tela de seleção do gate completo, reaproveitando render de créditos com restauração alpha aprovado. Diagnóstico limitado deve retornar automaticamente ao jogo para não confundir ausência de seleção com travamento; validar resposta direcional/A separadamente da ativação170ponteiros. Não repetir teste de menu/boot já aprovado.
- SELECTOR_TEST2 continua reprovado por tela preta; causa exata não demonstrada. Preservar pulos/câmera TEST3/30FPS/PT. Interface multilíngue completa e dublagens seguem pendentes.
- Este bloco registra aprovação; nenhum novo executável gerado.


## 07/10/2026 — NAVEGATION_PROBE entregue para separar tela/controle (06:02 UTC)
- Pacote SM64_DIAGNOSTICO_NAVEGACAO_IDIOMAS.zip, Library libfile_cada55ab9c508191ab463180bb545587.
- XEX SHA-256 0cabc1d2f258796ea2474a75901e07d0cc8f9a478c50bde118796f2bea368b64; ZIP 0501670b4ca27c2a009fb67b58906a6c30c613b0aac3c98a5ab04b6fcdcaaff3; PE 10c303127aefc0505dd19731115f1879b0bfe2bae2490999f471ec0ddec9199e.
- Gate424 bytes deriva do render/texto com alpha restaurada aprovada. Desenha Português/Español/English, marcador, lê D-pad e A, mas NÃO chama ativação nem altera os 170 registros; permanece PT e retorna automaticamente após300 frames (~10s) ou A. Pulos/câmera/30FPS/PT preservados.
- CPU/build PASS em casos sem botão, timer299/300, cima/baixo, seleção e A; round-trip exato; somente hookCD128 e cave3BC900 permitidos. Relatório docs/NAVIGATION_PROBE_2026_10_07.json; código e harness publicados.
- Hardware pendente. Informar se tela apareceu, se marcador respondeu, se A abriu e se o jogo abriu sozinho após ~10s. Se falhar, registrar tela exata; não atribuir causa sem evidência.
- Este teste não é edição multilíngue final: selecionar Español/English não troca diálogos. SELECTOR_TEST2 segue reprovado por tela preta; CREDITS_MENU_CORRIGIDO segue aprovado.


## 07/10/2026 — NAVEGATION_PROBE sem seletor visível no Xbox (06:10 UTC)
- Feedback real Pedro: executável ficou preto por alguns segundos, depois entrou nos créditos iniciais originais e na tela de apertar Start; nenhuma tela Português/Español/English apareceu.
- NAVEGATION_PROBE não aprovado como teste de tela/navegação. O boot/retorno ao jogo ocorreu, mas não há evidência de que a tela de idiomas tenha sido renderizada ou que D-pad/A tenham sido exercitados.
- Não atribuir ainda a falha a texto, controle ou ativação. O diagnóstico local desenhava escolhas, mas o resultado de hardware mostra que esse caminho não ficou visível antes do script original. Investigar ordem do hook/estado e diferença entre tela de créditos original e gate limitado.
- Próxima ação: criar instrumentação/diagnóstico ainda mais isolado, com marcador visual mínimo e estado persistente, ou revisar a chamada do hook para garantir que a rotina permaneça antes do script original. Preservar CREDITS_MENU_CORRIGIDO, pulos/câmera/30FPS/PT; não repetir NAVEGATION_PROBE sem mudança técnica.


## 07/10/2026 — VISUAL_PROBE entregue após seletor invisível (06:11 UTC)
- NAVEGATION_PROBE mostrou boot, créditos originais e Press Start, mas nenhuma tela de idiomas; não validou D-pad/A. Não repetir sem mudança.
- Novo pacote SM64_DIAGNOSTICO_VISUAL_TEXTO_CONHECIDO.zip, Library libfile_b5feeed62fd081919728fe097e389d1a, XEX6f10b64bc82235d04a0469c9a58324f5fd9b6ac276a93d429ac317d292bd2dd1, PE71eaaf63519a8580d7b4ad6b7013f04ae7897ebc52cc51584e1d4afc303903f6, ZIP7715c09db480156e2290822af781e0d4b3d42b14210f9f2cd173a308654ad74e.
- Usa o ponteiro de texto .lang+0x40 já aprovado no console, desenhado nas cinco posições da tela de seleção, sem ativar idioma nem depender dos textos PT/ES/EN. Após ~300 chamadas retorna ao script original. Round-trip exato; base TEST3/pulos/câmera/alpha preservados. Hardware pendente.
- Se texto conhecido aparecer: problema anterior está nos ponteiros/strings específicos do seletor. Se não aparecer: investigar hook/estado/render da tela. Não afirmar causa antes do resultado.


## 07/10/2026 — nova direção aprovada: seletor na tela pós-créditos
- Pedro autorizou abandonar as tentativas de entrada antes da tela de crédito e não usar mais o hook pré-créditos como caminho do seletor.
- Fluxo desejado: créditos universais intactos → tela atualmente equivalente a “Aperte Start” → mostrar Português / Español / English → D-pad seleciona → A confirma e executa o fluxo normal de Start/seleção de arquivo já aprovado.
- Objetivo técnico: adaptar a rotina original da tela “Aperte Start”, aproveitando sua renderização e controles existentes, em vez de criar uma tela pré-jogo independente. A confirmação deve chamar a ativação dos 170 ponteiros antes de entrar no fluxo do jogo.
- Nenhum executável foi gerado neste bloco. Próxima ação: localizar/mapear com evidência o endereço da rotina de título no XEX, validar seu contrato de retorno e só então construir candidato sobre a base TEST3/CREDITS_MENU_CORRIGIDO. Preservar 30FPS, PT, pulos/câmera, menu e saves.


## 07/10/2026 — fluxo pós-créditos aprovado para implementação
- Pedro aprovou: créditos universais → tela pós-créditos equivalente a Press Start com Português/Español/English → A confirma idioma → painel/pop-up de créditos personalizados já traduzido → A continua para menu normal de saves.
- A seleção deve ativar os 170 ponteiros antes do menu, preservando save, menu, pulos A/B/Y, câmera, PT e 30FPS. O painel de créditos deve creditar Nintendo/jogo original, port Xbox 360, localização/tradução/dublagens e PeterKleizoon — PMCN Studios.
- Removido como direção: qualquer seletor antes dos créditos. SELECTOR_TEST2/NAVEGATION/VISUAL probes não são base de produto; diagnósticos históricos preservados apenas como evidência.
- Documento técnico: docs/POST_CREDITS_LANGUAGE_FLOW_2026_10_07.md. Nenhum executável novo neste bloco.
- Próxima ação: mapear intro_regular/lvl_intro_update no XEX e implementar em fases: tela/confirmar, ativação, créditos personalizados, retorno ao file select.


## 07/10/2026 — início do mapeamento da rotina Press Start
- A arquitetura pós-créditos foi aprovada e documentada em docs/POST_CREDITS_LANGUAGE_FLOW_2026_10_07.md.
- A fonte recuperada confirma que o fluxo normal é `intro_regular` → `print_intro_text` → botão START → retorno 100 (file select) e `run_level_id_or_demo`; esse caminho deve ser preservado.
- O XEX não possui símbolos de função utilizáveis no ELF recuperado; o endereço da rotina precisa ser localizado por análise de código/cross-references antes de patch. Nenhum executável novo foi gerado.
- Próxima ação: mapear o ponto de chamada de `intro_regular`/`lvl_intro_update`, criar uma rotina de teste mínima no fluxo Press Start e só depois integrar ativação/ créditos multilíngues.


## 07/10/2026 — PERSISTENT_SELECTOR_PROBE entregue
- Os probes anteriores chegaram ao fluxo original sem mostrar a tela de idiomas. Nova versão remove o avanço automático: a rotina permanece na tela de teste até A; só então marca retorno ao script original na chamada seguinte.
- Pacote SM64_DIAGNOSTICO_SELETOR_PERSISTENTE.zip, Library libfile_588051e22f588191abf752efb8a63241. XEX1c53eeeb489bf64551143f0c03e2cdcf3fd68ee7a2c5413d87192c8aaf2c08b0; ZIP0b78d2695d880d0145e5ca0b4aa6994926a74bf07217cd658a75dee37aaa3ac4; PE828fe915dcab20ef13d95732746c03ae07a6ef93cf71080c931da9b36f02a5e3.
- Roundtrip exato, base TEST3/pulos/câmera/menu/save/alpha preservados. Hardware pendente. O diagnóstico não ativa idioma; objetivo é comprovar se a tela customizada permanece visível quando o temporizador não pode encerrá-la.
- Se a tela aparecer: pressionar A entra no jogo; se não aparecer: pressionar A após10s confirma retorno e mantém a falha na renderização/hook. Não repetir probes temporizados.


## 07/10/2026 — PERSISTENT_SELECTOR_PROBE reprovado e linha encerrada
- Feedback Pedro: pacote ficou somente em tela preta, sem crash e sem resposta observável.
- Erro de estratégia: este diagnóstico ainda usava o hook pré-créditos/level_script_execute. Ele foi criado apenas como investigação, mas contrariou a arquitetura pós-créditos já aprovada e não deveria ter sido entregue como próximo passo do produto.
- Linha de probes pré-créditos encerrada: SELECTOR_TEST2, NAVEGATION_PROBE, VISUAL_PROBE e PERSISTENT_SELECTOR_PROBE não serão usados como base de implementação.
- Próxima ação correta: localizar e alterar a rotina original da tela pós-créditos/Press Start. Nenhum novo probe pré-créditos deve ser gerado.


## 07/10/2026 — TITLE_SELECTOR_TEST1 gerado no fluxo Press Start original
- Mapeamento estático encontrou a rotina original pós-créditos em VA 0x820D5F48: lê estado da introdução, desenha a tela, lê controller, retorna código que leva ao file select. O hook pré-créditos 0x820CD128 permaneceu original e intocado.
- Candidato SM64_30FPS_SELECTOR_POST_CREDITOS_TEST1.zip, Library libfile_4fd70c0f6b908191bcb92c1594d2b698. XEX ff03bdf4444330c8759f53b832a9e8f39d9329bbc4b66e83a212d3d10775344c; ZIP 91c75fb09f976fe2b5f77342d71396c54196cc9d222782771189b83603bd3d48; PE 9e0ec3d7dfd0c54b7f6741ee7f30340d2d88511ec597d8c1ccb48771f36f5946.
- Patch: entrada 0x820D5F48 desvia para cave 0x823BC900 (252 bytes); desenha três ponteiros .lang (ES/PT/EN atuais), D-pad muda seleção, A chama ativação 170 ponteiros em 0x823BC800 e retorna código 100 para file select. Créditos personalizados ainda não integrados neste TEST1.
- Build/roundtrip PASS; .lang/PT/pulos/câmera e hook pré-créditos preservados byte a byte. Hardware pendente; não afirmar funcionamento antes do teste Xbox.
- Próxima ação: Pedro testa créditos universais, tela seletor pós-créditos, D-pad/A, menu/save. Se funcionar, integrar painel de créditos personalizados multilíngues antes do file select; se falhar, localizar tela/retorno no fluxo original.


## 07/10/2026 — TITLE_SELECTOR_TEST1 reprovado no Xbox (07/10, 04:10 BRT)
- Feedback Pedro: nenhuma mudança visível na tela de créditos/Press Start; fluxo original entrou no menu e no jogo. Após obter uma estrela e retornar ao castelo, antes das opções de salvar, o jogo travou e exigiu reset do console.
- TITLE_SELECTOR_TEST1 NÃO aprovado e retirado da linha de testes. O patch em 0x820D5F48 não demonstrou ser a rotina correta de Press Start; não reutilizar esse endereço como se estivesse validado. A regressão tardia indica corrupção/contrato incompatível, mesmo com boot inicial normal.
- Não atribuir a causa exata sem análise adicional. Preservar como evidência: sem seletor, crash após retorno de estrela. Não pedir repetição do mesmo pacote.
- Próxima ação: voltar ao XEX original TEST3/CREDITS_MENU_CORRIGIDO como base; localizar a verdadeira função de título por cross-reference de `lvl_intro_update`/`intro_regular` e validar contrato de retorno antes de qualquer novo patch. Nenhum novo executável até essa confirmação.


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
- Arquivo encontrado por Pedro na pasta do jogo: dump de diagnóstico gráfico, não save/asset. SHA-256 `93350c14d91f5908aa00bfe753e01ca79a20e4f0ba65492d5b9ddc7a52c1b703`, tamanho 1.178.555 bytes.
- Evidências: cabeçalho `SM64 360 FRAME DUMP`, backbuffer 1280x720, 2.027 chamadas `gfx_sp_tri1`, encerramento `END (2027 gfx_sp_tri1 calls dumped; uncapped)`.
- Causa confirmada: a compilação de diagnóstico contém a combinação `BACK + START` para solicitar dump; isso está documentado em `docs/CONTROLES_XBOX360.md` e coberto por `controls_probe.py`. O arquivo pode aparecer após o flush no fechamento/retorno ao dashboard.
- Não apagar automaticamente nem distribuir no jogo; pode ser removido manualmente sem afetar save. Evitar BACK+START nos testes de produto ou remover o diagnóstico em uma futura build.
- Relatório: `docs/SM64_DUMP_DIAGNOSTICO_2026_10_07.md`. Nenhum XEX gerado nesta análise.
- Próxima ação permanece: cross-reference local com fluxo de registradores para wall-crawl e busca de pacote de amostras de dublagem; não reutilizar probes de seletor descartados.


## 07/10/2026 — primeiro wall-crawl restrito a paredes verticais
- Decisão operacional: começar somente com parede vertical. Analógico esquerdo move na parede, botão de agachar mantém aderência, soltar faz cair; analógico direito/câmera e A/B/Y permanecem intocados.
- Inclinações, tetos e transições só serão avaliados após estabilidade. Critérios incluem menu/save e retorno de estrela sem regressão.
- Especificação publicada em docs/WALL_CRAWL_WALL_ONLY_SCOPE_2026_10_07.md. Nenhum XEX alterado; 665 candidatos anteriores continuam apenas inventário. Próxima ação: fluxo de registradores/chamadas de colisão + harness estático.


## 07/10/2026 — pacote real de dublagem PT-BR recebido e BPS analisado
- Pedro forneceu SM64-PTBR-1.0-BMatSantos-Kosmus.zip (Library libfile_9e016d73140c8191990bad65594a864c) e https://www.romhacking.net.br/index.php?topic=1629.0. ZIP SHA256 6e85270ff7d694e0e14ce3f99e5e29cc290c480066602542104a72cee0aa07d1; patch SHA256 1a6a0d6acb3f9626d52ed8f6a71866007df059e494461984591887c509bef4a2.
- ZIP contém BPS, capa e dois leia-me; nenhuma amostra WAV/AIFF separada. Página confirma dublagem Mario/BMatSantos e Peach/Vihh_Art, edição Kosmus.
- CRC do patch validado. ROM fonte exigida: 8.388.608 bytes, CRC32 3CE60709; alvo 9.090.352 bytes, CRC32 AACB4011. Leia-me indica Super Mario 64 (U) [!].z64.
- Análise de proveniência reconstruiu 1.718.881 bytes sem fonte; 7.371.471 bytes permanecem dependentes da fonte. Dados parciais NÃO são ROM funcional; nenhum banco de voz identificado/decodificado, nenhum XEX gerado.
- Código: scripts/multilang/analyze_bps_partial.py; relatório docs/PTBR_BPS_ANALYSIS_2026_10_07.json. Próxima ação: obter do usuário ROM compatível ou já patchada, validar CRC, aplicar BPS e extrair bancos de áudio. Preservar tradução própria e não publicar ROM/áudio no repositório público. Crawling vertical segue pendente.


## 07/10/2026 — busca alternativa por vozes PT-BR
- Pedro informou não possuir ROM e autorizou nova busca. Consultados site do autor bmatsantos.github.io, repositorio BMatSantos/sm64-ptbr, Romhack Plaza e buscas por samples/audio/releases.
- Nenhum pacote de vozes separadas foi localizado nesta busca. README do autor exige ROM previa para extracao; site distribui patches. Acesso web direto a releases falhou, portanto ausencia de release nao foi comprovada.
- Proxima alternativa tecnica: localizar tabelas/bancos do patch e testar cobertura byte a byte das amostras, independentemente da cobertura da ROM inteira. Os 7.371.471 bytes desconhecidos da ROM total NAO provam que as vozes sejam irrecuperaveis. Ainda nao ha vozes decodificadas nem XEX novo.


## 08/10/2026 — avanço: localização do áudio no BPS
- Rastreamento executado: CTL original 0x57B720 → alvo 0x57F8D0; TBL original 0x593560 → alvo 0x597710. Não aplicar offsets originais ao alvo traduzido.
- CTL de 97.856 bytes: 3.348 conhecidos diretamente pelo patch, 94.508 dependem da fonte. Primeiro bloco de 512 bytes inteiramente desconhecido. Ainda sem banco completo ou voz decodificada; nenhum XEX alterado.
- Código scripts/multilang/map_bps_audio_anchors.py; relatório docs/PTBR_AUDIO_OFFSETS_2026_10_08.md na branch ativa.
- Pedro não possui ROM. Próxima ação: comparar tabelas e amostras originais do XEX base do projeto com dependências do patch, completando somente bytes com correspondência comprovada; alternativa é pacote de vozes dos autores. Não inventar bytes nem declarar áudio completo usando saída esparsa. Crawling vertical segue pendente.

## 09/10/2026 — auditoria XEX × BPS com binários reais (chat)
- Recuperados da Biblioteca o ZIP do patch PT-BR e o pacote Xbox 360 `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip`. Confirmados hashes do ZIP BPS e do BPS já registrados; XEX interno SHA-256 `6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0`.
- Descriptografado XEX2 Basic para imagem PE válida de 17.170.432 bytes, SHA-256 `bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56`; sem alterar executável ou saves.
- Foi criado `scripts/multilang/audit_bps_xex_overlap.py` e testes `scripts/multilang/test_audit_bps_xex_overlap.py` (4 testes locais PASS). Git blobs conferidos com os scripts executados; workflow `.github/workflows/test-bps-xex-audit.yml` criado, validação do workflow remoto ainda deve ser consultada antes de declarar PASS no CI.
- Regiões: CTL 3.348 conhecidos / 94.508 desconhecidos; prefixo TBL 96 conhecidos / 477.392 desconhecidos; região TBL candidata 1.563.468 conhecidos / 44.516 desconhecidos, sem fixar limite real do banco.
- Varredura byte-exata no PE: 853 probes de 16 bytes, 853 de 32 bytes e 800 de 64 bytes; 0 hits para as três janelas. Probes amostrados; fragmentos conhecidos são do **alvo patchado**, portanto ausência de hits não invalida presença das amostras originais no XEX.
- Evidências: `docs/PTBR_XEX_AUDIO_AUDIT_2026_10_09.md` e `.json`. Próxima ação: estudar formato/bancos de áudio internos do PE e metadados CTL/ADPCM para confrontar estruturas com provas, não transplantar bytes adivinhados. Alternativa: samples autênticos dos autores.
- Ainda **nenhum arquivo de voz decodificada**, **nenhum XEX novo**, crawling vertical pendente e base 30 FPS preservada.

- Validação GitHub Actions confirmada em 09/10/2026: [Audit BPS-XEX provenance tests — run 37888054012](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37888054012), conclusão **success**; logs registram 4 testes PASS. Isso valida o parser e testes sintéticos, não uma extração de voz ou boot no Xbox.


## 09/10/2026 — NOVO: VADPCM identificado no patch e no Xbox 360
- Analisados binários reais recuperados. `scripts/multilang/scan_vadpcm_partial.py` encontrou 71 runs conhecidos >=512 bytes na região exploratória do TBL; **62/71 com 100% de headers VADPCM plausíveis** a cada 9 bytes em alguma fase, **63/71 >=95%**; 147.609 quadros inteiramente conhecidos somados nos 62 trechos. Isto NÃO identifica 147.609 vozes nem garante fronteira de amostra.
- Primeiro fragmento 0x60C040..0x60D9E8 contém **729 quadros inteiros** com padrão de header coerente. Dados estão comprimidos e a decodificação requer codebook/metadados vinculados.
- 43 candidatos a janelas de coeficientes CTL (27 com 62/64 bytes e 16 com 63/64 bytes). Nenhum dos 43 completo, não preencher desconhecidos.
- Foi inspecionado PE de XEX SHA-256 `bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56`: no offset 0xA27D20 há assinatura de livro VADPCM order2/predictors2 e 64 bytes de coeficientes. No offset 0xA3FB10 há 64/64 headers VADPCM, com 562/576 bytes não nulos e 159 valores distintos.
- `scripts/multilang/inspect_xex_sound_layout.py` identifica 452 **candidatos** de codebooks completos no PE (alinhamento, cabeçalho e coeficientes); comparação mascarada de 43 janelas do patch contra 452 candidatos do XEX: **0 matches**. Formatos compatíveis, porém a tabela de dublagem ainda depende de bytes ausentes. Não declarar voz extraída/decodificada.
- Relatório verificável: `docs/PTBR_VADPCM_STRUCTURAL_AUDIT_2026_10_09.md`. Novos scripts, dois conjuntos de testes e dois workflows publicados na branch ativa. CI: [scanner, 5 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37958461771) e [XEX, 4 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37958879757).
- Próxima ação: resolver **referências/pointers reais e IDs de voz dos bancos 08/0A do XEX**, e confrontar estruturas de sample, codebook, loop e tuning com patch; sem suposições nem substituições de áudio. Nenhum XEX novo, nenhum teste em console, base 30 FPS intacta.

## 09/10/2026 — organização PMCN Xbox 360 (somente documentação)

- A pedido do proprietário, criado [resumo simples](docs/STATUS_PARA_PEDRO.md) para explicar progresso, versões e próxima ação sem depender de histórico de chats. README em `main` e nesta branch apontam para a branch ativa e para o [painel central de desenvolvimento Xbox 360](https://github.com/PedroMarioaBros/OpenXeChain-X360-Builder/blob/main/docs/PAINEL_PMCN_XBOX360.md).
- Separados explicitamente: **toolchain OpenXeChain na nuvem** (compila código), **ferramentas de reconstrução XEX e testes estáticos de SM64**, **executável PT-BR aprovado pelo proprietário** e **produto multilíngue ainda não entregue**.
- Nenhum código, patch, asset, XEX, ROM, dublagem ou save do SM64 foi alterado. Sem novo teste ou lançamento para Xbox. A seleção trilíngue, extração de vozes e crawling continuam pendentes, e a linha 30 FPS é preservada.
- A próxima tarefa técnica segue a mesma: mapear com evidências reais IDs de voz → samples → codebooks/metadados dos bancos Xbox 08/0A, sem produzir voz falsa; separadamente, resolver o seletor pela rotina Press Start correta sem reutilizar hooks rejeitados.
- Um **GitHub Actions verde não equivale a jogo funcional**. O fluxo de compilação atual do SM64 no GitHub cobre utilitários e auditorias, não entrega automatizada de XEX multilíngue final.

## 09/10/2026 — QUATRO prévias de vozes PT-BR decodificadas (com prova condicional)
- Foram descobertos os índices CTL/TBL completos do PE no XEX de teste: offsets **de arquivo** 0xA27B90 (CTL) e 0xA3F9D0 (TBL), VAs respectivas 0x82A3AB90 e 0x82A529D0 (RVA muda 0x13000 na seção .data). 38 bancos de cada tipo.
- Bancos 08 e 0A do XEX original: **50 amostras válidas** (08: 27/27; 0A: 23/24 com **slot físico 03 nulo**). Descritores, sample addresses, livros e loops inspecionados.
- Fontes N64 de áudio parcialmente substituídas pelos blocos equivalentes do port com **máscara de proveniência**; nenhum valor desconhecido forjado. Alvo BPS recuperável subiu de **1.718.881** para **3.361.841** bytes; CTL **96.951/97.856** conhecidos, região TBL **2.216.388/2.216.704** conhecidos. Não comprova CRC completo da ROM fonte N64 exigida pelo patch.
- Dos 50 eventos, **4 foram decodificados em WAV experimental** com sample + livro ADPCM + descritor + loop estritamente conhecidos: 08/04 Mario Yahoo (0,773s), 08/06 Mario Hrmm (0,497s), 0A/02 Mario Panting (0,568s) e 0A/09 Mario Punch Yah (0,335s). Saídas PCM da versão Python e de uma implementação C independente foram **iguais byte a byte** nos quatro casos. Não declarar dublagem validada sem audição humana e confirmação de origem.
- O ZIP dos 4 WAVs + LEIA-ME/manifesto SHA foi salvo na Biblioteca **privada** `/Xbox360 - SM64 PTBR/SM64_PTBR_4_PREVIAS_EXPERIMENTAIS_2026-10-09.zip`, Library id `libfile_e46daa6cc8788191ba06e1cf87af923c`, SHA-256 `fca8f45be1faa5dec5aeea81200f5e5beb36c32e91b3e2931a2945dd1a30011d`. Não publicar os áudios no GitHub.
- Código da branch: `scripts/multilang/reconstruct_ptbr_audio_from_xex.py`, `scripts/multilang/test_reconstruct_ptbr_audio_from_xex.py`, relatórios `docs/PTBR_VOICE_RECOVERY_2026_10_09.md` e `.json`. [GitHub Actions](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37966469573): **6 testes sintéticos PASS**, logs conferidos.
- **Próximo passo:** ouvir WAVs; mapear por offset/proveniência as **905 lacunas restantes no CTL** e **316 na TBL** e buscar recuperação comprovada das partes necessárias para outras amostras. Não reconstruir source desconhecido nem compilar novo XEX especulativo. Base estável 30 FPS, menu/save, canhão e PT-BR do usuário intactos.


## 09/10/2026 — NOVO CHECKPOINT: 6 WAVs experimentais e lacunas BPS rastreadas
- **Padding XEX recuperado:** CTL completo estendido `0x17E00 → 0x17E40` (+64 bytes zero observados no PE, que terminam exatamente no início do TBL); TBL estendido `0x21D2F0 → 0x21D300` (+16 zeros). Nenhum valor inventado. O alvo BPS passou de **3.361.841** para **3.361.921 bytes conhecidos**.
- **Lacunas restantes:** CTL 841 bytes em 63 trechos (97.015/97.856 conhecidos); TBL 316 bytes em 34 trechos (2.216.388/2.216.704 conhecidos). **1.157/1.157 bytes desconhecidos restantes apontam para posições da ROM fonte fora do CTL/TBL original recuperado**, conforme rastreamento SourceRead/SourceCopy/TargetCopy.
- Bancos de vozes: 08 (CTL 405 desconhecidos, TBL 207); 0A (CTL 436, TBL 109). Auditoria reprodutível: `scripts/multilang/trace_audio_dependency_gaps.py`, `docs/PTBR_BPS_AUDIO_GAPS_2026_10_09.md` e `.json`. CI de rastreio [4 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37967913594).
- Os **quatro WAVs experimentais anteriores** (08/04 Yahoo, 08/06 Hrmm, 0A/02 Panting, 0A/09 Punch Yah) são distintos dos samples do XEX original nos mesmos slots (SHA-256 diferente). Isso comprova dados diferentes, não áudio validado por escuta.
- **Mais dois WAVs reais exportados SEM preencher gaps:** 08/16 Mario So Longa Bowser, 3.794 quadros VADPCM, 1,265s de quadros; 0A/04 Mario Dying, 5.438 quadros, 1,813s de quadros. Ambos possuem 100% dos bytes comprimidos e do codebook; os **metadados de loop não estão completos**, portanto a duração exata do evento dentro do jogo não é comprovada. PCM Python e C independentes **iguais byte a byte nas duas gravações**; ambas diferentes do XEX original.
- Novo script `scripts/multilang/decode_vadpcm_without_loop.py` e testes; CI [5 testes novos + 6 existentes, 11 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37968449638), logs verificados.
- **Seis prévias WAV no total, ainda não aprovadas por escuta.** ZIP privado consolidado, com 6 WAVs/manifesto/LEIA-ME: `/Xbox360 - SM64 PTBR/SM64_PTBR_6_PREVIAS_EXPERIMENTAIS_2026-10-09.zip`, Library id `libfile_986a0b2fe0b88191aa466ed03292d4ec`, SHA-256 `cfc024aac266f5da8905e38139f6e7ba01762af5b8738735686cd917d7f79a10`. Não publicar conteúdo áudio/ROM/XEX no GitHub público.
- Detalhes e hashes: `docs/PTBR_SIX_VOICE_PREVIEWS_2026_10_09.md` e `.json`.
- Próximo passo: (1) validar por escuta os seis WAVs; (2) tentar encontrar redundância autêntica para lacunas dos bancos 08/0A, sem supor coeficientes/frames; (3) somente integrar quando houver confiança de origem e reprodução. **Nenhum novo XEX**, base estável 30 FPS, PT-BR própria, saves e canhão preservados. O CRC da ROM original N64 fonte exigida pelo BPS segue não verificado.


## 12/10/2026 — CRASH CONFIRMADO após estrela / teste binário de isolamento entregue
- Pedro testou novamente `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip`: **letras/texto de menu corretos, mas Fatal Crash ao pegar uma estrela e voltar ao castelo**. RETIRAR a classificação antiga de versão aprovada/estável globalmente: apenas menu corrigido, gameplay regressado. Esta compilação NÃO deve ser sugerida como versão estável.
- Compilação falha: XEX SHA-256 `6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0`, PE SHA-256 `bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56`.
- Recuperado pacote TEST3 original da Biblioteca. XEX SHA-256 `b90ae1d1be953c1f817e9c64286c67da855778ac7c671098a3cd8495d8b6afd9`, PE SHA-256 `a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c`.
- **Comparação exata:** os PEs diferem somente no BL em offset `0xCD128` (TEST3 `4bfc8321` chamada original `level_script_execute` vs créditos `482ef7d9` gate próprio) e no code cave `0x3BC900..0x3BCA08` (264 bytes reservados; 222 não zero no build falho). **226 bytes efetivamente distintos**, 0 diferenças fora destas duas áreas. Reverter estas duas regiões produz PE **idêntico byte a byte ao TEST3**.
- **Resultado do teste no console do TEST3 para estrela→castelo: AINDA PENDENTE.** A hipótese principal é efeito colateral do hook de créditos, não causa demonstrada ainda. Testes estáticos anteriores apenas simulavam `level_script_execute` e não reproduziam todo o ciclo no hardware.
- Pacote privado A/B entregue `SM64_30FPS_TESTE_ISOLAMENTO_CRASH_ESTRELA_TEST3.zip`, SHA-256 `02df1f67fba83e9d1cdd5f60ef3924f4fc48c58adb4555b372e69f2270d39893`. Contém o **XEX original intacto TEST3** (sem recompilação/assinatura nova), instruções de testar em pasta separada e JSON de comparação. Biblioteca `/Xbox360 - SM64 PTBR/SM64_30FPS_TESTE_ISOLAMENTO_CRASH_ESTRELA_TEST3.zip`; libfile `libfile_0b550c3cf5b481919d988f4e302fc2c5`.
- Relatório `docs/STAR_RETURN_CRASH_2026_10_12.md`; script auditável `scripts/multilang/audit_star_return_regression.py`, testes `scripts/multilang/test_star_return_regression.py`. [CI 4 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38205019787) em dados sintéticos (verificados logs); PASS significa isolamento binário, NÃO boot/estrela no Xbox.
- Próxima ação imediata: **Pedro testa retorno após estrela no pacote TEST3**. Se passar, reprojetar créditos/seletor dentro da intro legítima sem hook global de level_script_execute; se falhar, investigar save/retorno e base TEST3. Não integrar alterações em cadeia sem prova.
- Áudio PT-BR: seis WAVs experimentais (4 com loop, 2 sem loop) continuam disponíveis em pacote privado; faltam escuta/identidade/integração e demais vozes. Manter frente de áudio separada da regressão. **Nenhum XEX novo com dublagem** e 30 FPS preservado.


## 12/10/2026 — PRIORIDADE ATUAL: TRADUÇÃO PT-BR / ES / EN, CONTROLES XBOX 360, SEM DUBLAGEM
- **Nova autorização do proprietário:** priorizar a edição única com Português/Español/English, **textos equivalentes em significado** e referências a botões sempre do Xbox 360. **Dublagem das vozes adiada**, inclusive os seis WAVs experimentais.
- **RESULTADO REAL DO TESTE A/B ANTERIOR:** Pedro confirmou que o XEX TEST3, sem hook de créditos, funcionou **perfeitamente** ao pegar estrela e retornar ao castelo. O CREDITS_MENU_CORRIGIDO falhou no mesmo caminho. Causa pontual ainda não localizada, mas regressão associada apenas a hook global em `0xCD128` e code cave; **NÃO reutilizar essa alteração em novos candidatos**.
- **Traduções já localizadas:** fontes originais EN `n64decomp/sm64@9921382a`, ES `Reonu/ultrasm64-spanish@b720e832` fixadas no repo; corpus de **170 diálogos EN e 170 ES** realmente importado em GitHub Actions. PT-BR do XEX v0.4 da PMCN permanece canônico e **não foi alterado**. Outra tradução espanhola Blade133bo v4.1 encontrada para comparação, mas adaptada de SM64 DS e NÃO usada automaticamente.
- **Controles Xbox:** `scripts/multilang/localize_controller_texts.py` processa 170 diálogos/idioma (não apenas índices preselecionados), ajusta referências ao analógico esquerdo/direito e botões A/X/LT-LB/RB-RT; validação fail-closed na presença de tokens N64. **34 diálogos de controle revisados**, incluindo ES ID149 com stick de movimento explicitado só na fonte ES.
- **Equivalência de instruções corrigida:** `scripts/multilang/es_semantic_errata.py` conserta diálogos ES 015 (chute A→X), 030 (redação), 032 (vestir gorro antes de voo), 034 (instruções A, câmera RB/RT, placas), 046 (salto contra parede com A). Substituições ancoradas por texto exato, falham se a fonte mudar; PT-BR e EN narrativo não mudam.
- **Catálogo de nomes de fases/missões EN/ES** implementado em `scripts/multilang/import_course_catalog.py`: 15 fases principais × 6 atos = **90 missões**, 10 entradas secretas, 1 cabeçalho de estrelas do castelo, 7 textos auxiliares, IDs e ordem alinhados. Corrigida grafia espanhola `ISLA FLOANTE` → `ISLA FLOTANTE`.
- **Auditoria automatizada:** `scripts/multilang/audit_language_parity.py`: 170 IDs, cobertura semântica básica das ações dos botões, 0 classes de botão ausentes, 0 tokens N64, 0 referências analógicas N64 ambíguas. **Não** prova equivalência editorial completa EN/ES/PT.
- **CI REAL:** [Trilingual Text and Xbox Controls Audit — 38333296556](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38333296556): 8 testes de erratas + 5 de botões + 5 de fases **=18 PASS**, mais validações reais do corpus EN/ES **PASS_INPUT_CLASS_COVERAGE** e **PASS_STAGE_ID_ALIGNMENT**. `Multilang Static Check` novamente PASS. Relatório `docs/TRILINGUAL_TEXT_PARITY_2026_10_12.md`. Não existem novos arquivos proprietários no GitHub.
- **O QUE FALTA:** revisão humana de significado e termos nas 3 versões; mapear UI/menus e integrar course catalogs no runtime (atualmente só fontes geradas em `_localization_build`); seletor na rotina legítima da intro, **não** hook global de level_script_execute; compilar XEX 30 FPS com hashes e testar em hardware seleção 3 idiomas → textos → fase → estrela → volta ao castelo → save. **Nenhum novo XEX liberado nesta etapa.**


## 12/10/2026 — TRÊS IDIOMAS: TABELAS REAIS DA TEST3, PPC EMULADO E DELTA ES/EN PROTEGIDO
- Pedro autorizou prosseguir com **textos PT-BR/ES/EN equivalentes e controles Xbox 360**, dublagem adiada. **TEST3 continuou estável** no teste real estrela→castelo; não ressuscitar hook global causador do Fatal Crash.
- **Descoberta no PE TEST3 original** XEX SHA `b90ae1d1be953c1f817e9c64286c67da855778ac7c671098a3cd8495d8b6afd9`, PE SHA `a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c`:
  - Tabela real de **26 nomes de fases** em offset mapeado `0x9E8C70`, SHA-256 dos ponteiros `3b789baca2d6d547c0f8f2985e96da24b4878944c1278d092c614d53934cbc9d`;
  - Tabela real de **90 nomes de estrelas** em `0x9E9620`, SHA-256 `ed5c7e598cade70bcfda05d3293b230a449650f9b45bf1f52572749640be30b0`. Ponteiros originais PT-BR efetivamente verificados, inclusive Fortaleza do Esmagão/Detonando a Parede. No curso, slot 24 é especial vazio, slot 25 é Segredos do Castelo.
  - A própria TEST3 **JÁ CONTÉM 170 diálogos PT-BR/ES/EN** na nona seção RW `.lang` de RVA `0x01040000`, magic `SM64LANG` v2, tabelas a offsets `0x100/0x3B0/0x660`. Uso `0x18D4E` de `0x20000` (29.362 bytes ainda livres). Os quatro glifos novos ES `ñ Ñ ¡ ¿` também estão instalados.
  - **Esses textos ES armazenados na TEST3 são VELHOS**, anteriores às erratas EN/ES de 12/10: o diálogo ES 015 ainda omite A+X para chute. NÃO chamar o conteúdo antigo de localização final correta.
- `scripts/multilang/install_trilingual_course_tables.py`: acrescenta `COURSE3` à .lang existente, tabelas PT/ES/EN de 26 fases e 90 estrelas, copia ponteiros PT originais sem qualquer mudança; falha se SHA PT não corresponder ao XEX TEST3, se a ordem dos cursos divergir ou se não couber na seção. **Não injeta hook**. [7 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334053320).
- `scripts/multilang/course_table_activation.py`: rotina PPC isolada **148 bytes** (SHA `f7cd86fb68725d8aa6f4c6fb5d9c9de7274434fa48f9d19368b3c78edb40d67b`) projetada para `0x823BCC00`, sem hook instalado; recebe r3=0 PT,1 ES,2 EN e copia 26+90 ponteiros. [PowerPC Unicorn **PASS** PT/ES/EN, entrada inválida 99 e -1](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334216661), inclusive verificação de sentinelas adjacentes. **Emulação CPU não equivale a teste Xbox.**
- `scripts/multilang/patch_existing_lang_dialogs.py`: atualização diferencial: compara novas strings ES/EN revisadas aos 170 textos já embarcados, anexa somente divergentes e corrige apenas os ponteiros desses IDs. SHA esperado dos 170 ponteiros PT `b612518417970dcf93904dc023aededcba046f9b1d0f823cf1beb799ee6c5a97`; SHA do pool PT intocado `614f3e4aa7eca2f657757a4ff8ef790c7deb5bf7426837f0e1ce94be673b69a8`. **Falha antes de qualquer saída se tocar em PT-BR, bytes originais do jogo ou estourar espaço.** [6 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334793668).
- **Documentação de engenharia:** `docs/TRILINGUAL_COURSE_RUNTIME_2026_10_12.md`; código/testes/CI na branch feature. Nenhum XEX, tradução integral externa, ROM ou áudio publicado no repositório público.
- **Situação sem fantasia:** mapeamento XEX REAL + scripts de montagem seguros + função PPC realmente emulada; os novos nomes de fases e diálogos revisados ainda **NÃO ESTÃO INSTALADOS EM UM NOVO XEX**, e o seletor da tela de título ainda não está ligado. Próximo: obter os corpora revisados do pipeline na construção local com a TEST3, rodar `install_trilingual_course_tables` e `patch_existing_lang_dialogs` no PE mapeado, localizar rotina intro_regular/lvl_intro_update para conexão sem hook global, round-trip XEX, testes usuário menu→fase→estrela→castelo→save **nos três idiomas**.


## 12/10/2026 — TEST3 TRILÍNGUE: INTEGRAÇÃO DE DADOS REAL PASS
- PE original TEST3 (17.170.432 bytes, SHA `a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c`) preservado. PE intermediário de dados tri-idioma SHA `96abbfb76775f4184b24106c1b78a1409ac1d9ace8bf5fa61a98af76a1b9eed8`: 26 nomes de áreas + 90 estrelas por idioma (PT/ES/EN) e 20 diálogos ES corrigidos; EN e PT 170/170 sem alterações. Todos os 858 ponteiros de diálogos+áreas/estrelas verificados. Espaço .lang restante: **13.841 bytes**. NENHUM byte de código de jogo fora .lang alterado, nem os hooks causadores dos crashes.
- Falha real `EXTRA_TEXT` com chaves convertidas para strings via JSON detectada e corrigida no importador; teste round-trip e [CI PASS 38335811493](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38335811493).
- ZIP privado recuperável, mas **NÃO JOGÁVEL (é PE, não XEX)**: `/Xbox360 - SM64 PTBR/SM64_TEST3_TRILINGUAL_DATA_STAGING_PRIVADO_2026-10-12.zip`, libfile `libfile_d1affc8caa3c819193c8e2db0f6bb29e`, SHA `dec42ea2228d0b52e16ec900f1314fe8fbc66da241e9ecde723abdf2c5af6c6c`.
- Evidências técnicas [relatório detalhado](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TRILINGUAL_REAL_TEST3_STAGING_2026_10_12.md). Próximo: seletor seguro na intro sem hooks anteriores, menus, XEX roundtrip, validação no Xbox nos 3 idiomas com estrela→castelo→save. Dublagem adiada.

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


## 17/10/2026 — TEST5 REPROVADA EM HARDWARE; TEST6 DIAGNÓSTICO VISUAL (NÃO É SELETOR NOVO)
- Pedro testou TEST5: boot, créditos, Aperte Start, menu de saves e jogo PT-BR abriram; **nenhum seletor** Português/Español/English apareceu, tal qual TEST4. **TEST5 FAIL no requisito principal**; não há resultado de estrela→castelo desta versão.
- Auditoria PE real: TEST5 PE SHA `a6c0a1c451f6dd114f73bd324cb297d42f3ed6f6c027c8237d3244284e622672`; hook `482754b9` realmente presente em `0x147448`; wrapper realmente presente em `0x3BC900`; `.lang+0x14` inicia em zero no arquivo. Portanto, a afirmação anterior de causa resolvida foi **prematura**: testes do wrapper isolado não demonstram que o título real o executa. Start avançou normalmente, então código do seletor não controlou a abertura observada. Causa runtime ainda em investigação, sem afirmar culpa do usuário.
- **TEST6 diagnóstica XEX REAL disponível**, sem tentar corrigir seletor: `SM64_TEST6_DIAGNOSTICO_TITULO_TESTE6_30FPS.zip`, SHA ZIP `e3c580683b4d2167e9ca5d888b950c587e456ffcbf0cbc0501383867aa3e470f`, XEX SHA `6089bee0bad628fb61e2ec7b97dc59a4e42c0eacba6d0d0a31bd145e9d5f087e`, PE SHA `98ec2515a57af928a91369b0cac24a4448aa619d95da63314162afb200a20e4f`. XEX rebuild Basic + round-trip PE **byte-idêntico PASS**, ZIP CRC PASS.
- Apenas **12 bytes diferentes TEST5→TEST6**, nos dois recursos ASCII de título: offset PE `0x778` `APERTE`→`TESTE6` e `0x1C98` `APERTE START`→`TESTE6 START`. Nenhuma mudança de controle, hook, diálogos, gameplay/save/PT-BR dos diálogos ou dublagem. Marcador diagnóstivo temporário deve ser revertido nas builds futuras.
- ZIP privado preservado em `/Xbox360 - SM64 PTBR/SM64_TEST6_DIAGNOSTICO_TITULO_TESTE6_30FPS.zip`, Library `libfile_c8eb020b0ce88191b0ca7c059e374cf1`, **não publicado GitHub**.
- Código/testes `scripts/multilang/test6_title_marker.py`, `test_test6_title_marker.py`, [CI de marcadores PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39003135765). Relatório `docs/TEST5_FALHA_TEST6_MARCADOR_2026_10_17.md`.
- **Único teste agora:** Pedro extrai TEST6 em pasta separada, abre e informa se o texto do título mostra `TESTE6` ou segue `APERTE START`. Não precisa abrir save/fase. `TESTE6` visível prova recurso carregado; `APERTE` pode indicar outro recurso desenhado ou outra cópia carregada, não inferir erro do usuário.
- Dublagem permanece estritamente FORA do escopo até aprovação hardware PT/ES/EN + seletor + save/estrela, seguida de nova autorização.


## 17/10/2026 — TEST6 PASS VISUAL REAL: "TESTE6 START" APARECEU NO XBOX; SELETOR AINDA FALHA
- Pedro enviou **duas fotos do Xbox 360**: na segunda, o título original exibe claramente **"TESTE6 START"** (substituição intencional de "APERTE"). **TEST6 MARKER VISUAL PASS REAL**. A primeira mostra a cabeça do Mario normal. **Nenhum seletor de idioma aparece**. Não confundir teste de marcador com implementação funcional.
- Esse resultado **descarta hipótese de estar carregando somente a TEST5 intacta**, pois o novo texto foi renderizado. Não é prova de execução do wrapper `0x823BC900`. TEST4, TEST5 continuam FAIL seletor; TEST3 continua única base hardware aprovada para estrela→castelo.
- Nova âncora técnica comprovada: `print_intro_text` em `0x82098D18` chama `print_text_centered` em **`0x8212B498`** para desenhar o título. A rotina é chamada dentro de **`intro_regular` em BL `0x821472D4`** e também dentro de **`intro_game_over` em BL `0x82147368`**. Ambas ficam ANTES da checagem de Start. A função global `print_intro_text` também é usada nos demos, portanto não substituí-la indiscriminadamente em gameplay.
- **Próxima abordagem:** antes de outra "versão funcional", prova visual/teste a partir dessas duas chamadas específicas para renderização nativa do título, usando o formato de strings ASCII da UI (não presumir compatibilidade com charmap de diálogos). Se comprovada, integrar navegação/ativação PT/ES/EN e preservar TEST3 original e saves, sem hooks globais que causaram crash.
- Relatório [TEST6_HARDWARE_MARKER_PASS_2026_10_17.md](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST6_HARDWARE_MARKER_PASS_2026_10_17.md). **Nenhuma TEST7 criada nessa análise**. Dublagem segue estritamente bloqueada.


## 17/10/2026 — TEST7 PRONTA (DIAGNÓSTICO DO CAMINHO DA INTRO), TEST6 MARCADOR CONFIRMADO POR FOTOS
- As fotos de TEST6 no Xbox mostram claramente **TESTE6 START**. Isso comprova novo texto carregado/renderizado, mas NÃO a execução do wrapper do seletor. TEST4 e TEST5 tiveram **falha real do seletor**; não marcar funcional.
- **TEST7 diagnóstica XEX real já construída:** ZIP `SM64_TEST7_DIAGNOSTICO_ABERTURA_NORMAL_30FPS.zip` SHA `de470eafeeae6be5ac6c1717405c69790e7892d3bbb98834ac79215d8204ba43` (17.184.703 bytes); XEX `default.xex` SHA `089b887abc702359729249bdecb49d09f1412fd450aad6fc42739c7d3d5a9b81`; PE SHA `cee2a0cbb4bbb7b47e867e387b13f81e71e72a2f60134851abedc9bfbd4986aa`. Roundtrip AES XEX→PE byte-exato PASS, ZIP CRC PASS.
- **Apenas 6 bytes realmente diferentes da TEST6:** marcador `TESTE6`→`TESTE7` em 0x778 e 0x1C98 (2 bytes), mais substituir BL `4bf51a45` em `intro_regular→print_intro_text` offset mapeado `0x1472D4` por PPC NOP `60000000` (4 bytes). Chamada `intro_game_over→print_intro_text` em `0x147368` original, todos os dados trilíngues, controls B/Y, saves, gameplay, áudio, hook global e wrapper seletor **intocados**.
- **Objetivo EXCLUSIVAMENTE diagnóstico:** no Xbox, abrir TEST7 em pasta isolada e observar se aparece "TESTE7 START" na tela do Mario. Se **NÃO** aparecer, a abertura normal é fonte do texto e foi interceptada pela alteração → investigar estado/runtime wrapper. Se **APARECER**, o texto é desenhado por outro caminho (Game Over ou demo ou equivalente) → parar de hookar intro_regular às cegas. Se crashar, parar testes. Não precisa abrir save ou jogar.
- Backup ZIP privado no Library `/Xbox360 - SM64 PTBR/SM64_TEST7_DIAGNOSTICO_ABERTURA_NORMAL_30FPS.zip` (id `libfile_ef25c163ece0819188b997a64fcdc6eb`); **não publicar binários do jogo no GitHub**.
- Script público `scripts/multilang/test7_intro_path_probe.py` com hashes e guardas, testes `test_test7_intro_path_probe.py`, [GitHub Actions CI 39007791041 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39007791041). [Relatório](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST7_DIAGNOSTICO_CAMINHO_INTRO_2026_10_17.md).
- **TEST7 não é seletor funcional**; ainda não testada no console, e TEST3 continua única base com estrela→castelo PASS real. Dublagem estritamente fora de escopo até jogo trilíngue aprovado integralmente e nova autorização.


## 17/10/2026 — TEST7 (OPÇÃO A) APROVOU CAMINHO DA IMPRESSÃO; TEST8 VISUAL PRONTA
- **Resultado real informado por Pedro na TEST7:** apareceu o rosto do Mario, mas NÃO apareceu `TESTE7 START` (opção A). A BL de `intro_regular → print_intro_text` em `0x821472D4` é uma âncora comprovada de exibição de título no Xbox. TEST4 e TEST5 continuam FAIL no seletor; TEST6 mostrou `TESTE6 START`.
- O título real usa `print_text_centered` `0x8212B498`, **ASCII terminado por NUL**, enquanto o antigo menu usava outra função e dados no charmap de diálogo. Isso pode explicar o seletor invisível, mas ainda falta teste visual do overlay nativo.
- **TEST8 XEX real DIAGNÓSTICA pronta**, NÃO é seletor interativo: `SM64_TEST8_VISUAL_IDIOMAS_30FPS.zip` SHA ZIP `5fbd56533f6c211d6ef87785cf83eb047dcb77d2a669805e7a5c1158e4d7e4a7` 17.184.919B, XEX SHA `006b662635b41f8a0e2996a8fbba43ab354acdca11ed21c184e6bf669daa1ccb`, PE SHA `fab6a7c31d1fa2cb4aea3ad5e0f3171bde5248a13f48bbcab56d2bc05fc4c438`. XEX Basic AES→PE byte-idêntico PASS; ZIP CRC PASS.
- Sobre TEST7: restaurada BL do dispatcher errado `0x82147448`; em `0x821472D4` chamada de print original substituída por wrapper PPC de **112 bytes** em cave livre `0x823BCD00`. Wrapper chama `print_intro_text` nativa e `print_text_centered` quatro vezes, tentando mostrar `IDIOMAS TESTE8`, `PORTUGUES`, `ESPANOL`, `ENGLISH`. Labels sem acentos e maiúsculas são provisórias do teste; **não há navegação/seleção/ativação de idioma nesta TEST8**. PTBR, EN/ES, B/Y, saves e gameplay preservados; somente 148 bytes efetivamente diferentes na PE em intervalos allowlist.
- Segurança: primeira região `0x823BCF00` rejeitada pela guarda, pois colidia com código já existente em `0x823BD000`; movido a `0x823BCD00` inteiramente livre. [**5 testes GitHub Actions PASS, run 39008801116**](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39008801116).
- ZIP TEST8 está na Biblioteca privada `/Xbox360 - SM64 PTBR/SM64_TEST8_VISUAL_IDIOMAS_30FPS.zip`, ID `libfile_9e708b07a3248191bfda3be2e3c6a211`. Código `scripts/multilang/test8_native_title_visual.py`, [relatório](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST7_A_CONFIRMADO_TEST8_VISUAL_2026_10_17.md).
- **Próximo teste no Xbox:** executar somente TEST8 em pasta própria, observar se aparecem QUATRO linhas de idiomas junto do Mario ou só TESTE8 START; se crashar interromper. Não precisa abrir save/fase. **Dublagem inteiramente fora do projeto até jogo multilíngue e seletor aprovados e nova autorização expressa.**


## 17/10/2026 — TEST8 VISUAL **PASS** NO XBOX (FOTOS); TEST9 SELETOR INTERATIVO XEX PRONTA, HARDWARE PENDENTE
- **TESTE REAL DO USUÁRIO:** duas fotografias do Xbox mostrando claramente as quatro opções da TEST8 `IDIOMAS TESTE8`, `PORTUGUES`, `ESPANOL`, `ENGLISH`. Em uma delas, `TESTE8 START` ainda visível. Portanto **TEST8 PASS VISUAL**, MAS NÃO interação nem troca de idioma; usuário mostrou sobreposição das letras coloridas com boné/rosto do Mario. Não declarar TEST8 seletor funcional.
- **Nova TEST9 XEX Basic candidata experimental REAL:** ZIP `SM64_TEST9_SELETOR_FUNCIONAL_CANDIDATO_30FPS.zip`, SHA `01ef0d3de8eead10960665268daccf5d7b944bd10e741c7facdaf6d7ee98abbc`, 17.189.374 bytes. XEX `default.xex` SHA **`1b29d111f234df0515c0a21e964bf9866061c4688d4f0b2a74e741a61c320f07`**, PE SHA `a405ba6e97c933298a1e24361423b7230f75957a4ee0c0ecfced21d957b2e641`; round-trip XEX AES→PE **exato** e ZIP CRC **PASS**. Preservada em Biblioteca privada `/Xbox360 - SM64 PTBR/SM64_TEST9_SELETOR_FUNCIONAL_CANDIDATO_30FPS.zip`, ID `libfile_91fb0786f8188191ab908711b38534a9`. ZIP inclui fonte do construtor, README e JSON de auditoria.
- **A TEST9 NÃO FOI TESTADA NO XBOX!** Implementação no callback de impressão `intro_regular`, já provado por TEST7/TEST8. Wrapper PPC em `0x823BCD00`, 384 bytes SHA **`7198267b6f0e7699f5226637cd5db7e5f9470d5b5f3b9aac69e8d6e2ac0db6b1`**: desenha `IDIOMAS, PORTUGUES, ESPANOL, ENGLISH, A CONFIRMAR` numa coluna menor à esquerda; mostra marcador `X` ao lado da opção; D-pad UP/DOWN cicla; máscara Start até confirmar; **A** ativa 170 ponteiros de diálogo, 26 nomes de áreas e 90 estrelas de PT/ES/EN; após A volta a chamar impressão original `APERTE START` e Start normal. Acentos da tela de seleção são provisórios até adaptação dos glifos nativos. Não mexeu em gameplay, B/Y, save, PT-BR ou hook global que causava crash.
- Endereço do controle **confirmado pelo disassembly**: `0x823C8990` (opcode original `lis r11,0x823D; lwz r11,0x8990(r11)` usa imediato COM SINAL). Não confundir com `0x823D8990`.
- **8 testes PPC/source PASS** [Actions 39010452532](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39010452532) = 5 CPU reais emulados + 3 guardas/reproducibilidade, nenhum dos quais é teste Xbox. Código `scripts/multilang/test9_selector_native.py`, `test_test9_ppc_runtime.py` e `test_test9_source_build.py`. Diferenças TEST8→TEST9 **343 bytes**, confined 0x3BCD00 (wrapper), 2 strings TESTE8→APERTE, cursor .lang e novas strings curtas, ponteiros PT/ES/EN byte-idênticos.
- [Relatório integral](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST8_VISUAL_PASS_TEST9_INTERATIVO_2026_10_17.md). **Teste pedido ao Pedro**: iniciar em pasta separada, tela de idiomas/indicador X, Start antes de A deve NÃO avançar, D-pad UP/DOWN deve mover X, A confirma, depois Start abre saves; somente após isso conferir diálogos/estrela→castelo para cada idioma. No primeiro crash interromper.
- **Dublagem 100% fora do escopo** até todos idiomas, seletor, saves e gameplay estáveis aprovados no Xbox e nova autorização expressa.


## 17/10/2026 — TEST9 FALHOU COM FATAL CRASH NA TELA DO SELETOR (CONFIRMAÇÃO DO PROPRIETÁRIO)
- Pedro testou TEST9 no **Xbox 360 real**. O jogo abriu e passou os créditos iniciais, porém deu **FATAL CRASH ao entrar na tela onde deveria aparecer o seletor de idiomas**. **TEST9 REPROVADA. NÃO pedir novo teste da TEST9**, não declarar que o seletor funcionou e não promover a XEX como release.
- **Referências seguras:** TEST8 exibiu quatro opções visualmente (PASS visual documentado em fotos do Xbox) e é a última base de intro visual aprovada; TEST3 é a última base com teste de estrela→castelo PASS real.
- Inspeção real TEST8→TEST9 confirma 343 bytes alterados: wrapper 112→384 bytes na cave `0x3BCD00`, strings `TESTE8`→`APERTE`, cursor e 3 novas strings ASCII .lang. Callsite intro `0x1472D4`, título `0x147448`, `level_script_execute` `0xCD128`, ponteiros PT/ES/EN e B/Y **permaneceram iguais**. Na TEST9 a novidade perigosa inclui ler o ponteiro de controle em `0x823C8990`, escrever `buttonPressed` via `sth r8,0x12(r11)` para mascarar Start, aceitar DPad/A, ativar pools e desenhar marcador. **Ainda não sabemos qual mudança causou o crash**; tratar a escrita do controle como suspeita prioritária, não causa provada.
- Emulação anterior de 5 casos **PPC32** passou, mas não representava todo o ambiente Xbox PowerPC64. Novo probe PPC64 `scripts/multilang/probe_test9_ppc64_mode.py` com Unicorn 2.1.4 resultou `UC_ERR_EXCEPTION errno=21` **antes de executar qualquer instrução** (contador 0), logo o probe é **INCONCLUSIVO**, não reproduziu Fatal Crash do console. Não usar seu retorno como diagnóstico causal.
- **Não gerar TEST10 indiscriminadamente.** Próximo passo: construir regressões que isolem render, leitura do controle, mutação da estrutura de input (evitar escrita direta em `buttonPressed`) e posterior troca dos ponteiros, sempre partindo da TEST8 que passou. Priorizar uma instrumentação que não arrisque saves ou gameplay, separar estados e apresentar um único candidato justificado ao proprietário depois da auditoria.
- [Relatório técnico](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST9_FATAL_CRASH_2026_10_17.md) com bytes/hashes/falha real. **Dublagem integralmente fora do escopo** até três idiomas + seletor + gameplay/saves aprovados no Xbox e nova autorização explícita.


## 17/10/2026 — TEST10 DIAGNÓSTICA DE LEITURA (SEM ESCRITA) GERADA APÓS FATAL CRASH DA TEST9
- **Hardware confirmado:** TEST9 deu FATAL CRASH ao chegar na tela de idiomas após os créditos iniciais. NÃO retestar TEST9. TEST8 é última exibição visual aprovada no Xbox (quatro rótulos), TEST3 última build com estrela→castelo PASS no console.
- **Ainda não sabemos a causa exata do Fatal Crash.** TEST9 introduziu simultaneamente ler/escrever controller->buttonPressed, DPad/A, Start gate e troca das tabelas, além de alteração do overlay. O probe PPC64 Unicorn resultou `UC_ERR_EXCEPTION` **antes de primeira instrução** e é INCONCLUSIVO, não reproduz o crash.
- **TEST10 XEX real criado a partir da TEST8** (sem usar TEST9): ZIP `SM64_TEST10_DIAGNOSTICO_LEITURA_CONTROLES_30FPS.zip`, SHA `51e6ca289a2e58d30d9e3cc7bf0648ab7f96798332f040d97c0757771bc10347` 17.189.927 bytes, XEX SHA `ffa460aab10a0877f084289d7cf1e3b3aa44078d3afc8d7b0919a81ba1a2cfab`, PE SHA `15423bd657f438e0e90f1744a8af5b5aad8f07b72eb5eaadf96655f99b0b604c`. AES round-trip XEX→PE **byte-idêntico PASS**, ZIP CRC PASS.
- **O QUE FAZ:** mantém intro TEST8 nativa e rótulos coloridos, mostra `TESTE10` e um **X temporário** na linha PORTUGUES enquanto D-pad UP for mantido, ESPANOL enquanto DOWN, ENGLISH enquanto A. Só **leitura de buttonDown em controller+0x10**, sem escrever no controle, **sem bloquear Start, sem selecionar idiomas, sem trocar textos ou mexer em saves/level_script**. Wrapper PPC 204 bytes, SHA `4fd27ff93e2ed0140a849e971b0a9bcdcd39f0b86665506f0af8c78a956b4a6f`. Apenas **94 bytes efetivamente alterados no PE** comparados com TEST8, confinados a overlay/cursor e novos rótulos ASCII; 170 diálogos PTBR e tabelas EN/ES/Star preservados.
- **CI [39012707192](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39012707192) PASS 5 testes PPC32**: UP/DOWN/A, controle nulo, Start original preservado, não modifica buttonPressed. Não comprova hardware PPC64.
- **Binário privado recuperável** na Biblioteca `/Xbox360 - SM64 PTBR/SM64_TEST10_DIAGNOSTICO_LEITURA_CONTROLES_30FPS.zip`, ID `libfile_93000491b92c8191b2e4f2f882c5bbe3`. Scripts fonte e testes publicados em GitHub sem PE/XEX: `scripts/multilang/test10_controller_read_probe.py`, `scripts/multilang/test_test10_readonly.py`, CI `test10-controller-readonly.yml`.
- **TESTE DO PROPRIETÁRIO PENDENTE:** colocar TEST10 em pasta própria, abrir até rosto Mario, sem saves. Reportar se mostrou `TESTE10` e se marcador X segue UP/DOWN/A. Se Fatal Crash interromper e não executar de novo. Em caso de PASS, próximo passo implementar índice/seleção sem escrita em buttonPressed; se FAIL, isolar leitura do controller primeiro. [Relatório](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST9_CRASH_TEST10_CONTROLLER_READONLY_2026_10_17.md).
- **DUBLAGEM CONTINUA FORMALMENTE FORA DO ESCOPO** até jogo com traduções PT/ES/EN, seletor realmente funcional e gameplay/saves aprovados no Xbox e nova autorização expressa.


## 17/10/2026 — TEST10 REPROVADA: 3 FATAL CRASHES AO APERTAR UP / DOWN / A
- **Resultado de hardware explícito de Pedro:** TEST10 abre, mostra créditos e a lista de idiomas; analógico direito não muda nada (não havia binding previsto); ao pressionar D-pad UP deu Fatal Crash. Após reboot, D-pad DOWN deu Fatal Crash. Após outro reboot, botão A deu Fatal Crash. **Três falhas nas três tentativas. NÃO solicitar nova execução da TEST10.**
- A TEST8 segue referência de **renderização visual aprovada** dos idiomas no Xbox; TEST3 segue referência de **jogabilidade e retorno de estrela ao castelo aprovado**. TEST9 Fatal Crash ao abrir seletor; TEST10 Fatal Crash ao tentar qualquer botão que deveria desenhar o X; ambas reprovadas.
- Inspeção PE TEST10 real: wrapper PowerPC `0x823BCD00`, 204 bytes SHA `4fd27ff93e2ed0140a849e971b0a9bcdcd39f0b86665506f0af8c78a956b4a6f` **não escreve na memória do controle**. Lê ponteiro em `0x823C8990` e `buttonDown` em `+0x10` inclusive nos quadros sem botão. Quatro chamadas nativas `print_text_centered` desenham textos constantes nos endereços wrapper `0x823BCD20/34/48/5C`; **uma quinta chamada em `0x823BCDB8` só ocorre após qualquer dos bits D-pad UP 0x800, DOWN 0x400 e A 0x8000**, para imprimir a string `X\0` existente em VA `0x8305CA24`. Portanto **a hipótese de que a TEST9 travou simplesmente por escrever em buttonPressed foi enfraquecida**; a TEST10 trava sem fazer essa escrita. A suspeita prioritária agora é o caminho de renderização X extra/ABI/contexto (não causa provada).
- [Auditoria estática/5 testes PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39014488596) `scripts/multilang/test_test10_postmortem_paths.py`: verifica wrapper real de 204B, quatro render fixos + quinto condicional, bits de botões, nenhuma escrita em controller. **Os testes NÃO reproduzem o crash Xbox**.
- Referência `src/game/print.c` upstream indica `sTextLabels[52]` e `print_text_centered` aloca no pool de efeitos; não assumir limite de quatro/cinco rótulos sem evidência real do port Xbox.
- **NÃO criar TEST11 às cegas.** Próxima análise: separar o reconhecimento do botão da quinta chamada gráfica. Um futuro teste mais seguro poderá manter **exatamente quatro chamadas de desenho por quadro**, escolhendo texto para um dos slots existentes conforme os botões; sem escrita em controller, sem bloquear Start, sem seleção ativada até esse caminho ser aprovado. Inspecionar a ABI PPC64 e o contexto gráfico do jogo. Nenhuma dublagem; tradução/seleção PT/ES/EN permanecem prioridade.
- [Relatório TEST10 hardware](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST10_FATAL_CRASH_BUTTONS_2026_10_17.md). Estado **TEST10 FAIL HARDWARE** agora substitui "PENDING" em todos os resumos.


## 17/10/2026 — XENIA LOCAL REAL REPRODUZIU CRASH TEST9/TEST10; TEST11 1 BYTE CORRIGE, PT/ES/EN TÍTULO PASS NO EMULADOR

**RESULTADOS COMPROVADOS (emulador Xenia Canary Linux dac2794; Vulkan Mesa software llvmpipe; XEX real privado)**:
- TEST9 XEX original: crash sem input em título `PC=0x8215F1A4`, `Access Violation read at 0x0000000100000000`.
- TEST10 original: mesmo crash ao pressionar A e D-pad UP no Xenia, como comportamento de Fatal Crash observado em hardware real. TEST9 (Xbox crash antes selector) e TEST10 (Xbox crash no UP, DOWN, A) continuam oficialmente REPROVADAS. Não retestar fisicamente.
- Glifo do seletor **`X` era o gatilho**: `print_text_centered("X")` entra em caminho de textura com leitura nula. Trocar **APENAS O BYTE do marcador** `X→A` em TEST10 exibiu A após botão sem crash; em TEST9 `X→O` exibiu O, sem crash. A entrada exata da tabela de textura ainda não foi validada estaticamente; causa relacionada ao glifo X é comprovada por teste A/B real em Xenia.
- Correção definitiva desta falha específica: em TEST9 PE mapeado offset **`0x105CA30`**, guest VA **`0x8305CA30`**, ASCII `0x58` (X) → `0x4F` (O). **Exatamente 1 byte da imagem interna PE alterado**, sem novas rotinas/hooks/áudio. SHA PE original `a405ba6e97c933298a1e24361423b7230f75957a4ee0c0ecfced21d957b2e641`; SHA PE novo **`a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`**. Reconstrução AES XEX2 Basic e round-trip ao PE **byte-idêntico PASS**.
- **TEST11 XEX privada CANDIDATA real**: `SM64_TEST11_SELETOR_TRILINGUE_GLIFO_SEGURO_CANDIDATA_30FPS.zip`, ZIP SHA **`175f8ab3dbb510827cde7d4156acd7f2f72c6beb482344a84ed2e813622d74d1`**, 17.185.804 B, XEX SHA **`ff5a669976865a8ddf9e9f4a4158c19c05db7de682b316905cef8771343752f7`**, XEX 17.182.720 B. Backup privado Library `/Xbox360 - SM64 PTBR/SM64_TEST11_SELETOR_TRILINGUE_GLIFO_SEGURO_CANDIDATA_30FPS.zip`, ID **`libfile_dc328d27eba08191b669d85ac3e8e1c7`**. Não foi nem deve ser anunciada como APROVADA em Xbox: **hardware PENDENTE**.
- **Em Xenia TEST11 fez corretamente:** Start BLOQUEADO antes da escolha; D-pad DOWN move O para ESPANOL, DOWN duas vezes para ENGLISH; A confirma e muda intro para APERTE START; Start posterior abre menu de saves; em Espanol, A no MARIO A iniciou cena Peach. PT, ES e EN até saves **PASS no Xenia sem crash dump**.
- **RESTRIÇÃO IMPORTANTE:** o menu de saves após Espanol permaneceu em **português** (ABRIR JOGO, COP, etc.), portanto **a localização trilíngue ainda NÃO está concluída**. Acentos do título, sobreposição de letras com rosto do Mario, painel de créditos, diálogos em fase, persistência de saves, coleta estrela→castelo para TEST11 seguem pendentes. **TEST3** ainda é única base com coleta de estrela→castelo PASS no Xbox; TEST8 continua overlay de título aprovado em Xbox real.
- Infra de automação corrigida: antigo binding Xenia `F5/F6/F7/F8` **ERA REJEITADO** (`failed to parse binding`) e F8 podia abrir UI pós-processamento. Usar `--hid=keyboard --keyboard_mode=1 --keybind_dpad_up=R --keybind_dpad_down=T --keybind_a=J --keybind_start=G` com X11 XTEST sob Xvfb. [CI Xenia teclado corrigido 39028670106 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39028670106). GitHub não contém executável do jogo.
- Patch reproduzível `scripts/multilang/test11_safe_title_cursor.py`, 5 testes da [CI de glifo TEST11 39028635499 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39028635499); relatório [TEST9_TEST10_XENIA_CRASH_CAUSE_TEST11_2026_10_17.md](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST9_TEST10_XENIA_CRASH_CAUSE_TEST11_2026_10_17.md).
- Evidências Xenia privadas em Library `/Xbox360 - SM64 PTBR/SM64_TEST11_XENIA_PROVAS_PRIVADAS_2026_10_17.zip`, ID `libfile_aeba11abe7688191a7dc9549fdac72f9`, SHA `599aa61f6d7dcb71293da0d5051ec03b40c4d4be759f771d1cf082a8e32a05b6` (somente capturas e trechos logs; nenhum XEX).
- **Próximo trabalho:** continuar regressões no Xenia com gameplay real até pegar estrela e voltar ao castelo, corrigir o file-select menu para PT/ES/EN e glifos/acento/layout, antes de dizer que jogo multilíngue está pronto; validacao física opcional e pontual posteriormente.
- **DUBLAGEM TOTALMENTE FORA DO ESCOPO** até PT/ES/EN e gameplay estáveis Xbox confirmados e nova ordem explícita.

## Retomada operacional — 18/10/2026

### Último resultado confirmado no Xenia (não confundir com aprovação em Xbox)
- TEST9/TEST10 originais reproduzem no Xenia Linux o crash de renderização no caminho do cursor X; TEST11 substitui somente o byte do cursor por O e passa os fluxos do título em PT/ES/EN no emulador.
- A automação de entrada válida é scripts/xenia/replay_buttons.py com R=D-pad UP, T=D-pad DOWN, J=A, G=Start. O antigo binding F5–F8 era inválido e seus resultados não são evidência de entrada no guest.
- TEST11 continua candidata, não aprovada em hardware. ZIP privado não deve ser publicado no GitHub.
- Pendência reproduzida no emulador: após selecionar Español, o menu de saves ainda exibe rótulos em português (ABRIR JOGO, PTS., COP., APAGA, ESTEREO). Ainda não se validaram diálogos de fases, persistência de saves e ciclo coletar estrela → retornar ao castelo nesta candidata. TEST3 continua referência física para o último fluxo; TEST8 para visualização da tela de idiomas.
- Testes anteriores do Xenia que usavam F5/F6/F7/F8 estão invalidados. Ver docs/TEST9_TEST10_XENIA_CRASH_CAUSE_TEST11_2026_10_17.md e workflow xenia-linux-keyboard-harness.yml.

### Próxima execução (não produzir outra build Xbox ainda)
1. Preservar o XEX TEST11 e suas capturas como baseline.
2. Auditar a origem dos rótulos do menu de saves no PE/strings e verificar se o código de seleção de idioma é consultado nesse caminho; não presumir que a tabela .lang de diálogos/cursos já inclua a UI de save.
3. Escrever testes estáticos e uma matriz de reprodução Xenia com inputs verificados R/T/J/G. Testar primeiro PT, depois ES e EN até menu de saves; recolher log e capturas em cada transição.
4. Investigar diálogos, salvar e coletar estrela/retornar ao castelo em Xenia, sem mexer no hook de gameplay estável.
5. Só criar nova candidata quando a origem da UI de saves e o plano de regressão estiverem definidos. Não pedir novos testes físicos até haver build justificada.
6. Não iniciar dublagem: continua expressamente fora de escopo até PT/ES/EN e gameplay estarem estáveis e o usuário autorizar novamente.

Status de confiança: a correção de cursor O foi observada em Xenia; não declarar TEST11 como aprovada em Xbox nem como localização multilíngue completa.


## 20/10/2026 — diagnóstico da lacuna de ativação multilíngue após TEST11
- O proprietário confirmou no Xbox físico que TEST11 inicia, percorre Português/Español/English e confirma com A, mas o prompt seguinte continua “APERTE START”.
- Análise estática dos scripts versionados: `pregame_gate.py` envia o idioma selecionado à rotina `ACTIVATE_LANGUAGE` (0x823BC800); `language_activation.py` só troca os 170 ponteiros dos registros de diálogo canônicos. `build_lang_section.py` não cria strings traduzidas para Press Start nem para os rótulos do menu de saves.
- Isso demonstra que os testes atuais de ativação não cobrem a UI de título/file-select; não demonstra que a troca dos 170 diálogos falhe. A tela Press Start e o menu de saves seguem caminhos de texto separados no código de referência.
- Relatório publicado: [docs/LANGUAGE_SELECTOR_ACTIVATION_GAP_2026_10_20.md](docs/LANGUAGE_SELECTOR_ACTIVATION_GAP_2026_10_20.md), commit do relatório `1b5111523bc16f14cae879940e939d81fb600b92`.
- Nenhum PE/XEX foi alterado ou gerado, e nenhum novo teste de emulação/hardware foi executado nesta etapa.
- Próxima ação: obter bytes reais da base/TEST11 e mapear por varredura estática os textos nativos e suas rotinas de renderização no PE Xbox 360. Só depois projetar patch para Press Start e file-select com testes fail-closed. Não transferir endereços da versão N64/MIPS. Manter TEST11 como referência física e não pedir novo teste ao proprietário ainda.


## 20/10/2026 — confirmação adicional de idioma English em hardware
- Relato direto do proprietário: escolheu English no seletor da TEST11 e confirmou com A. O prompt pós-seleção continuou “APERTE START”, mas **os textos dentro do jogo apareceram em inglês**.
- Esta evidência mostra que o idioma selecionado chega a pelo menos parte do sistema de textos; o diagnóstico não deve dizer que a ativação está totalmente quebrada. O problema confirmado é a inconsistência do prompt de título, que permanece PT-BR. Ainda não se sabe se todos os menus/textos acompanham o idioma.
- Status atualizado em docs/STATUS_PARA_PEDRO.md (commit 3e1096bd4b928188e90249dcdc8b1ce4c0db6aec).
- Aguardando o resultado do teste espanhol que o proprietário já está fazendo. Não pedir repetição do teste English e não gerar nova XEX antes de mapear com segurança as strings/rotinas do título.


## 20/10/2026 — especificação do comportamento dinâmico do seletor
- Ordem fixa: **English → Español → Português**.
- Ao abrir o jogo, English deve estar destacado por padrão.
- Ao mover o cursor para qualquer idioma, antes de apertar A, a tela do seletor deve atualizar todos os textos para o idioma destacado: título/etiqueta de idiomas, nomes de todas as opções e instrução de confirmação.
- A deve confirmar a escolha e manter esse idioma nos textos internos do jogo.
- Isso é requisito solicitado, ainda não implementado nem testado. Não confundir especificação com progresso concluído.
- O proprietário iniciou um teste físico de Español na TEST11; aguardar o relato sem pedir que repita o teste de English.


## 20/10/2026 — rótulos do seletor traduzidos pelo idioma destacado
- Ordem lógica fixa: inglês → espanhol → português; English fica selecionado por padrão ao abrir.
- **English:** `Languages`; opções `English / Spanish / Portuguese`; confirmação `Press A to confirm`.
- **Español:** `Idiomas`; opções `Inglés / Español / Portugués`; confirmação `Pulsa A para confirmar`.
- **Português:** `Idiomas`; opções `Inglês / Espanhol / Português`; confirmação `Pressione A para confirmar`.
- A tela inteira — título, nomes de todas as opções e instrução — deve trocar imediatamente ao mover o seletor, antes de A. Os rótulos não ficam fixos em inglês/espanhol.
- Requisito documentado, ainda não implementado/testado. Não gerar nova XEX antes da análise técnica e dos testes seguros.


## 20/10/2026 — teste físico confirmou os três idiomas; pendências de interface
- **Teste físico confirmado pelo proprietário:** depois de selecionar e confirmar, os textos internos aparecem em português, espanhol e inglês conforme o idioma escolhido. A ativação para os textos internos funciona nos três idiomas no teste relatado.
- **Não pedir repetição** dos testes dos três idiomas.
- Pendências: (1) English como idioma padrão ao abrir; (2) ordem fixa English → Español → Português; (3) ao mover o cursor, antes de A, traduzir toda a tela do seletor, inclusive o título, os nomes de todas as opções e a instrução; (4) após A, localizar o prompt “APERTE START”/Press Start; (5) localizar o menu de seleção de saves/file-select e todos os seus textos.
- Rótulos esperados conforme idioma destacado: English — “Languages / English / Spanish / Portuguese / Press A to confirm”; Español — “Idiomas / Inglés / Español / Portugués / Pulsa A para confirmar”; Português — “Idiomas / Inglês / Espanhol / Português / Pressione A para confirmar”.
- Não confundir sucesso da tradução dos textos internos com conclusão de todos os menus. Nenhuma nova XEX foi gerada. Próxima etapa: mapear com segurança strings e rotinas no PE Xbox 360, criar verificações estáticas fail-closed e só então implementar/testar, sem transplantar endereços N64/MIPS. Dublagem continua fora do escopo.


## 20/10/2026 — checkpoint de engenharia com PE TEST11 recuperada
- PE mapeada da TEST11 recuperada do pacote de teste e hash conferido com a auditoria: `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd` (17.170.432 bytes).
- Wrapper físico do seletor: `0x823BCD00`, 384 bytes, hash `7198267b6f0e7699f5226637cd5db7e5f9470d5b5f3b9aac69e8d6e2ac0db6b1`. Cave auxiliar `0x823BCB00–0x823BCBFF` está zerado na PE de referência.
- Mapeados o prompt dividido em `APERTE`/`START` e os offsets das strings do menu de saves. Ver `docs/TEST11_UI_TEXT_MAP_2026_10_20.md`.
- A variante alternativa `pregame_gate.py` tem testes de CPU aprovados para English padrão e ponteiros de prévia, mas não é o wrapper usado na TEST11 física. Não confundir com build de console.
- Próximo passo: construir patcher específico para a PE TEST11, localizar strings da prévia por idioma, prompt Start e menu saves; preservar `.lang+0x80–0x87` do scratch B/Y; executar testes CPU e Xenia antes de entregar nova XEX. Nenhuma nova XEX gerada nesta etapa.


## 20/10/2026 — TEST12: patcher específico da PE TEST11
- Criado `scripts/multilang/test12_live_ui.py`, com entrada estritamente fixada ao hash TEST11 e validações fail-closed.
- Execução local sobre a PE recuperada gerou candidata PE SHA-256 `50fd4a1f07dcfccd232debfa48e656ac3618b2a3d6a676ca570c12888224ec30` (não é XEX ainda).
- Wrapper PPC: 564/768 bytes; helper de localização de saves: 108/256 bytes; 21 strings de menu verificadas contra os limites dos buffers.
- CPU tests passaram: [workflow TEST12](https://github.com/PedroMarioaBros/SM64toX360/actions/workflows/test-test12-live-ui.yml). Testes cobrem prévia dinâmica, navegação, prompt Start, strings de saves e preservação B/Y.
- **Limite em aberto:** a prévia da fonte colorida ainda usa transliterações sem acentos; suporte seguro aos acentos precisa ser resolvido. Nenhum XEX novo foi empacotado ou validado em Xenia/hardware.
- Ver [relatório TEST12](docs/TEST12_STATIC_PATCH_REPORT_2026_10_20.md). Não considerar interface final até resolver acentos e testar XEX.
