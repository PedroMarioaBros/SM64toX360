# TEST14 — centralização, glifos, bloqueio de demo e prompt Start trilíngue

Data: 20/10/2026

## Estado

**TEST14 é uma candidata experimental empacotada, ainda não testada no Xbox físico.** A base é a PE mapeada da TEST13D, que o proprietário testou e confirmou visualmente: seletor aparece e aceita navegação/A; slots vazios exibem NOVO / NUEVO / NEW.

## Mudanças na candidata

1. Os cinco textos desenhados no seletor recebem coordenada central horizontal X=160: título, três opções e instrução de confirmação.
2. Os 15 rótulos/instruções da prévia (cinco textos por idioma) são gravados em ASCII maiúsculo, preservando tamanho e terminador NUL. Isso evita os glifos minúsculos u/g que o proprietário observou em cinza. A validação visual dessas letras precisa ser feita no console; os textos do seletor seguem sem acentos, pois o renderizador nativo utilizado espera ASCII/NUL.
3. Enquanto .lang+0x14 indica seletor ainda aberto (estado 0), o wrapper zera o contador nativo de demos em 0x82E52FE8. O contador é usado pelo helper nativo que pode iniciar a cutscene quando chega a 800 quadros. Depois de A confirmar o idioma, o contador volta ao fluxo normal do jogo.
4. A chamada alternativa de texto em 0x82147368 (caminho intro_game_over, original PPC 4bf519b1) é redirecionada ao mesmo wrapper do seletor, em 0x823BCD00, para que os idiomas ES/EN também possam localizar o prompt nas cutscenes.
5. Para abrir espaço ao wrapper, o helper de rótulo de save slot foi movido para 0x823BCB70, no cave compartilhado com o helper de menu. O helper de menu (108 bytes) permanece em 0x823BCB00; o helper de status (96 bytes) foi instalado após ele. A sequência de escrita foi corrigida para não apagar acidentalmente o helper de status.
6. Mantidos o mapeamento do idioma, os 170 diálogos, o hook global de fase, o scratch de B/Y e a base 30 FPS. Native60 e dublagem continuam fora de escopo.

## Integridade binária

- PE TEST13D de entrada: 17.170.432 bytes, SHA-256 0063a6dedb10b780c4e558f77af148bbf61bef0ae780f72647c112c2f44def9e.
- PE TEST14 candidata: 17.170.432 bytes, SHA-256 6266c97deec43d4f43fe3c89bce2ebfb019ab220409702a35fccbd17b0878742.
- Wrapper: 596 bytes, SHA-256 fbf0734348f9dd2986f4352ecdb6c9b3b7892499f4ec92cac2f30142252901a1.
- XEX TEST14: 17.182.720 bytes, SHA-256 a8f4aac287cafb7ddd68a2563284cc5583c9f318c4645704cab6d5cd6ccddbcb.
- ZIP TEST14: SHA-256 706603e38aa12ae34868eab327b6073cb6881628179507e444f2fafa0fafc858; ZIP integrity PASS.
- Roundtrip XEX2 Basic: a PE extraída da XEX reconstruída ficou **byte a byte idêntica** à PE candidata (hash 6266c97...8742).
- Diferenças efetivas TEST13D PE → TEST14 PE: 726 bytes; confinadas ao wrapper, helper de menu/status, callsite do status dos slots, chamada de prompt no caminho intro_game_over e texto de seletor já alocado no .lang. B/Y scratch, hook global de fase e chamada regular da intro foram verificados inalterados.

## Testes automatizados de fonte

No commit 30e3b93ea5def9373a22bbcaae1cf2684f9caf96:
- [TEST12 Trilingual UI Static and CPU Tests — PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39423432009). Verifica patcher, instruções PPC em Unicorn, posições X=160, strings maiúsculas, reset do temporizador somente no estado não confirmado e preservação do helper de slots.
- [Multilang Static Check — PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39423432106).

Esses resultados não validam a renderização física nem o fluxo do Xbox. A execução Xenia anterior da TEST13D também não validou imagem porque o ambiente gráfico falhou ao inicializar Vulkan. Não declaro PASS visual para TEST14.

## Teste físico requerido

Use pasta isolada, mantenha TEST12/TEST13D e os saves intactos:

1. Deixe o seletor ocioso por pelo menos 35 segundos: ele deve permanecer no seletor, sem entrar em demo/cutscene antes da confirmação A.
2. Confirme se todos os cinco textos estão centralizados e se nenhuma letra fica cinza em cada um dos três idiomas.
3. Confirme idioma com A. Para verificar o caminho alternativo de cutscene, escolha Español e depois English separadamente; após confirmar, deixe o título ocioso até começar o attract/demo (cerca de 27 segundos em 30 FPS) e veja se aparece PULSA START / PRESS START, respectivamente.
4. Confirme que slots vazios continuam mostrando NUEVO / NEW / NOVO.
5. Se houver tela preta, crash ou fluxo inesperado, parar e retornar à versão de rollback. Registre a última tela vista e o idioma selecionado.

Não publicar PE/XEX do jogo no repositório GitHub.