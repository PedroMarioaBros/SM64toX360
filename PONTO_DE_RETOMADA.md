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
