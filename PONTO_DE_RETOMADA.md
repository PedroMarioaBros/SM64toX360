# Ponto de retomada — leia primeiro
Branch ativa feature/multilang-dub-30fps; base30FPS. Leia AGENTS.md e CHECKPOINT_PROJETO.md. Atualize após resultados/antes de encerrar; publique e verifique.

07/10/2026: diagnóstico CRÉDITOS_MENU_CORRIGIDO aprovado no Xbox: jogo abriu, textos/informações do menu reapareceram, save carregou normalmente. Preservação alpha por quadro aprovada; não repetir esse teste. Último pacote SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip, libfile_ec3a76d126b88191a9f71e15d00fdf8b. Hashes/reprodução no checkpoint.

Pulos TEST3/câmera e diagnósticos de boot preservados. SELECTOR_TEST2 permanece reprovado: tela preta sem crash. Não atribuir sua falha à regressão alpha, que tinha outro caminho.

Próxima ação: isolar lógica estado/controller/tela seletor sobre render/alpha aprovado; diagnóstico limitado com retorno automático ao jogo. Separar navegação/A de ativação de170ponteiros e registrar evidências. Não declarar seletor corrigido sem hardware. Interface completa/dublagens pendentes; Native60 fora desta etapa.

[Checkpoint canônico](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/CHECKPOINT_PROJETO.md)
