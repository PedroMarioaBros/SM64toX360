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

## Resultado físico TEST14 — retorno do proprietário (20/10/2026)

O proprietário testou a candidata no Xbox 360 e informou:
- Seletor parado por mais de um minuto sem iniciar cutscene: **PASS** para a supressão de demo enquanto a seleção está aberta.
- Slots vazios continuam corretos: **NEW / NUEVO / NOVO**: PASS.
- Letras **G e U continuam cinza**, mesmo com os textos em maiúsculas: **FAIL**. A alteração de caixa não resolveu o problema; não repetir essa hipótese como solução. É necessário investigar o caminho/fonte de renderização e a cor/atlas dos glifos.
- Depois de confirmar English ou Español com A, o título mostra PRESS START / prompt esperado, mas quando entra na cutscene/attract demo, a tela volta a mostrar **APERTE START** em português: **FAIL**.

### Diagnóstico do prompt após o teste físico — corrigido em 20/10/2026

O texto antigo desta seção dizia incorretamente que o callsite `0x821472D4` permanecia intacto. Isso foi corrigido: a instrução em `0x821472D4` já é redirecionada para o wrapper TEST14, e a chamada em `0x82147368` também foi redirecionada. Mesmo assim, o proprietário observou `APERTE START` em português quando começou a cutscene/attract demo após selecionar English ou Español.

A evidência histórica do diagnóstico TEST7 também importa: ao substituir a chamada de `intro_regular` em `0x821472D4` por NOP, o texto de título esperado não apareceu no Xbox. Isso comprovou que esse caminho participa da exibição normal do título, mas não prova que seja o único caminho usado pela demo. Portanto, não instalar um segundo hook nesse endereço nem assumir que o problema é apenas a chamada `intro_regular` ou `intro_game_over`.

**Hipótese operacional atual:** existe um caminho adicional ou uma condição de estado que faz a demo desenhar o prompt português. Precisamos localizar outros callsites/referências de `print_intro_text` (`0x82098D18`) na imagem mapeada exata da TEST14 e verificar o fluxo de estado/idioma nesse caminho.

**Limitação concreta desta retomada:** o pacote TEST14 disponível contém `default.xex`, README e auditoria; não contém a PE mapeada separada. A PE exata esperada tem SHA-256 `6266c97deec43d4f43fe3c89bce2ebfb019ab220409702a35fccbd17b0878742`. Ainda não consegui reconstruir/recuperar essa PE a partir do XEX neste ambiente, portanto a varredura de callsites não foi executada. Não afirmar que outro chamador foi encontrado nem gerar um patch especulativo.

### Próxima correção visual

Não considerar “ASCII maiúsculo” solução para o G/U cinza. Identificar a rotina que efetivamente desenha a prévia e verificar se ela usa uma fonte/paleta ou índice de glifo em que G/U estão mapeados para a cor cinza. Só depois preparar uma mudança específica e testável. Nenhuma afirmação de correção visual até confirmação no Xbox.

## Correção do diagnóstico de callsite — 20/10/2026

Uma verificação adicional do patcher esclareceu que `0x821472D4` **já está redirecionado para o wrapper do seletor** na TEST14: a instrução `48275a2d` é exatamente o branch-and-link de `intro_regular` para `0x823BCD00`. Portanto, não é correto afirmar que o callsite regular ficou intacto nem instalar um segundo hook nele. A tentativa de adicionar um hook duplicado foi removida antes de gerar qualquer nova XEX; o fixture de teste exige que o branch do seletor original continue preservado.

O hook adicional de TEST14 em `0x82147368` também não resolveu o prompt físico. Conclusão atual: o prompt visto durante a cutscene/attract demo vem de outro caminho de renderização ou estado que ainda não foi isolado. A próxima etapa é mapear os demais chamadores da função nativa `print_intro_text` (VA `0x82098D18`) e verificar o estado do idioma no caminho de demo, sem sobrescrever o hook de seleção.

O teste de regressão voltou a ficar verde após remover a hipótese duplicada: [TEST12 Trilingual UI Static and CPU Tests — PASS, run 39427028860](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39427028860). Isso valida o patcher e os testes de CPU, não resolve o prompt no hardware.


## Complemento do proprietário — centralização confirmada e próxima investigação (20/10/2026)

O proprietário acrescentou uma observação que não havia sido registrada no retorno anterior: **os textos da tela de seleção ficaram centralizados exatamente como ele queria**. Registrar como **PASS visual no Xbox físico** para o alinhamento horizontal dos textos do seletor. Não reabrir a centralização como pendência nem alterá-la na próxima candidata, salvo se outra mudança comprovadamente a afetar.

### Próxima etapa técnica iniciada: diagnóstico, sem novo binário

O retorno físico separa quatro fatos: (1) centralização correta; (2) seletor permanece aberto por mais de um minuto; (3) slots NEW/NUEVO/NOVO corretos; (4) G/U ainda cinza e prompt de demo em português após escolher English/Español. A mudança para maiúsculas já foi refutada no hardware e não deve ser repetida.

Sobre o prompt: o wrapper TEST14 só substitui os caminhos conhecidos nos callsites `0x821472D4` e `0x82147368`, mas o segundo não resolveu o texto durante attract/demo e o primeiro já estava redirecionado na candidata. A próxima investigação é enumerar, a partir de bytes da PE mapeada correspondente à TEST14, os demais chamadores do destino nativo `print_intro_text` (`0x82098D18`) e rastrear como o estado/índice de idioma é lido durante demo. O mapeamento estático dos callsites ainda não foi concluído nesta etapa; não afirmar que o chamador alternativo já foi encontrado.

Sobre G/U: a hipótese de caixa foi falsificada pelo teste físico. Não há ainda evidência suficiente para atribuir o cinza à paleta, ao atlas ou ao mapeamento de glifos. A investigação deve identificar a rotina efetiva usada pelos textos de prévia e comparar o tratamento de G/U com letras vizinhas, sem trocar o renderizador às cegas. A experiência anterior com `PRINT_CENTER` + formato de string incompatível não deve ser usada como prova contra o caminho ASCII/NUL de TEST13D/TEST14.

**Nenhum XEX novo foi produzido nesta etapa.** A próxima build só deve ser montada após hipótese específica e verificável, testes estáticos/PPC verdes e auditoria dos hashes; base 30 FPS, PT-BR preservado, Native60 e dublagem fora do escopo.
