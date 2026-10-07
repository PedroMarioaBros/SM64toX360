# Ponto de retomada — leia primeiro
Etapa ativa: PT-BR / Español / English sobre v0.4 de 30 FPS.
Branch: feature/multilang-dub-30fps.
Leia CHECKPOINT_PROJETO.md e AGENTS.md antes de trabalhar. Atualize e verifique o registro remoto antes de encerrar cada sessão.

Estado em 07/10/2026: SELECTOR_TEST1 apresentou tela preta; NOHOOK abriu o jogo no Xbox, confirmado pelo Pedro. Seletor ainda não validado.
Próxima ação: corrigir PASSTHROUGH, pois o pacote anterior manteve o hook original e não isola o desvio. Verificar BL 0x482EF7D9 em 0x820CD128, branch imediato ao original na cave, round-trip e hashes; disponibilizar diagnóstico corrigido e registrar teste no Xbox. Não repetir NOHOOK.
Detalhes e histórico no checkpoint da branch ativa: https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/CHECKPOINT_PROJETO.md
