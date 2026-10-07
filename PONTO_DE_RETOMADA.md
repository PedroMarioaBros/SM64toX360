# Ponto de retomada — leia primeiro
Etapa ativa: PT-BR / Español / English sobre v0.4 de 30 FPS.
Branch: feature/multilang-dub-30fps.
Leia CHECKPOINT_PROJETO.md e AGENTS.md antes de trabalhar. Atualize e verifique o registro remoto antes de encerrar cada sessão.

Estado em 07/10/2026: SELECTOR_TEST1 apresentou tela preta; NOHOOK abriu o jogo no Xbox, confirmado pelo Pedro. Seletor ainda não validado.
Próxima ação: corrigir PASSTHROUGH, pois o pacote anterior manteve o hook original e não isola o desvio. Verificar BL 0x482EF7D9 em 0x820CD128, branch imediato ao original na cave, round-trip e hashes; disponibilizar diagnóstico corrigido e registrar teste no Xbox. Não repetir NOHOOK.
Detalhes e histórico no checkpoint da branch ativa: https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/CHECKPOINT_PROJETO.md


Atualização: PASSTHROUGH2 corrigido, reconstruído e verificado; disponível para teste do Pedro. Próxima ação atual: registrar se PASSTHROUGH2 abre diretamente o jogo ou apresenta tela preta. Hashes e recuperação no último bloco do checkpoint. Não testar PASSTHROUGH antigo.


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
