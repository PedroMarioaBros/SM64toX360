# Ponto de retomada — leia primeiro
Branch ativa feature/multilang-dub-30fps; base30FPS. Leia AGENTS.md e CHECKPOINT_PROJETO.md. Atualize após resultados/antes de encerrar; publique e verifique.

Pulos TEST3/câmera e boot diagnósticos preservados. SELECTOR_TEST2 reprovado: tela preta sem crash. CREDITS90 abriu jogo/save, mas menu sem texto: regressão não proposital, resultado parcial.

Erro identificado: diagnóstico zerava alpha de menu em cada quadro de delegação. Correção guarda/restaura alpha por quadro dos créditos e não altera no caminho original. Não prova causa da tela preta do seletor.

Próximo teste: SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip, libfile_ec3a76d126b88191a9f71e15d00fdf8b. CPU/build PASS; hardware pendente. Esperar~3s sem botões; registrar textos menu e carregamento save. Hashes/reprodução no último checkpoint.

Após menu aprovado, retomar lógica estado/controller e tela seletor com alpha preservada. Não repetir diagnósticos aprovados nem declarar seletor corrigido. Interface completa/dublagens pendentes; Native60 fora desta etapa.

[Checkpoint canônico](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/CHECKPOINT_PROJETO.md)
