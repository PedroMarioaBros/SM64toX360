# Continuidade canônica — SM64 Xbox 360
Atualizado: 07/10/2026. Repositório: PedroMarioaBros/SM64toX360.
Branch de desenvolvimento: feature/multilang-dub-30fps.

## Como retomar
1. Ler este arquivo e AGENTS.md antes de editar ou reconstruir.
2. Consultar os arquivos técnicos na branch de desenvolvimento; main é também entrada para descoberta.
3. Ler docs/PREGAME_GATE_STATIC_INTEGRATION_2026_10_05.json e os scripts citados abaixo.
4. Conferir a revisão remota e diferenças locais. Não repetir recuperação ou testes já comprovados sem motivo.
5. Próxima ação: corrigir e validar o diagnóstico PASSTHROUGH antes de testar o caminho do hook no Xbox 360. Atualizar este checkpoint após cada resultado relevante e antes de encerrar.

## Objetivo e decisões permanentes
Edição única baseada na v0.4 funcional de 30 FPS, com seleção Português / Español / English antes de qualquer tela normal.
PT-BR: preservar exatamente a tradução existente do usuário e comandos Xbox 360; posteriormente dublagem PT-BR.
ES: tradução completa, comandos Xbox 360 e posteriormente vozes espanholas.
EN: textos e vozes originais, com TODAS as referências a controles localizadas para Xbox 360.
Crédito: PeterKleizoon - PMCN Studios.
Não misturar Native60, não substituir PT-BR pela tradução pública BMatSantos, não usar o grande BSS de .data para os pools.
Nenhum teste estático ou em Unicorn equivale a funcionamento comprovado no Xbox.

## Onde estamos
STATUS: HARDWARE_BOOT_FAILURE_DIAGNOSTIC. hardware_verified: false.
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
- [ ] Se NOHOOK abrir, testar PASSTHROUGH: hook presente, desvio imediato ao original.
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
