# Continuidade canônica — SM64 Xbox 360
Atualizado: 05/10/2026. Repositório: PedroMarioaBros/SM64toX360.
Branch de desenvolvimento: feature/multilang-dub-30fps.

## Como retomar
1. Ler este arquivo e AGENTS.md antes de editar ou reconstruir.
2. Consultar os arquivos técnicos na branch de desenvolvimento; main é também entrada para descoberta.
3. Ler docs/PREGAME_GATE_STATIC_INTEGRATION_2026_10_05.json e os scripts citados abaixo.
4. Conferir a revisão remota e diferenças locais. Não repetir recuperação ou testes já comprovados sem motivo.
5. Próxima ação: registrar o teste real do pacote SELECTOR_TEST1 no Xbox 360. Atualizar este checkpoint após cada resultado relevante e antes de encerrar.

## Objetivo e decisões permanentes
Edição única baseada na v0.4 funcional de 30 FPS, com seleção Português / Español / English antes de qualquer tela normal.
PT-BR: preservar exatamente a tradução existente do usuário e comandos Xbox 360; posteriormente dublagem PT-BR.
ES: tradução completa, comandos Xbox 360 e posteriormente vozes espanholas.
EN: textos e vozes originais, com TODAS as referências a controles localizadas para Xbox 360.
Crédito: PeterKleizoon - PMCN Studios.
Não misturar Native60, não substituir PT-BR pela tradução pública BMatSantos, não usar o grande BSS de .data para os pools.
Nenhum teste estático ou em Unicorn equivale a funcionamento comprovado no Xbox.

## Onde estamos
STATUS: FIRST_HARDWARE_TEST_CANDIDATE. hardware_verified: false.
Novo candidato SELECTOR_TEST1 reconstruído, validado e disponibilizado para primeiro teste no console.
Os hashes históricos EN/ES seguem sem reprodução; essa pendência de rastreabilidade não foi declarada resolvida. O novo candidato foi validado independentemente com fontes fixadas, layout, ponteiros, preservação PT e round-trip.
Próximo requisito funcional: teste real do seletor pelo Pedro; corrigir eventual falha antes de integrar vozes.
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
- [ ] Teste Pedro no Xbox: boot → créditos → cada idioma → primeira tela/menu → diálogos → save existente/novo → salvar/sair; registrar feedback real.
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
