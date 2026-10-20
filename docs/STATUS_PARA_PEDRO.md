# SM64 Xbox 360 — situação atual (20/10/2026, após teste físico TEST14)

**Este resumo substitui o cabeçalho histórico abaixo como estado atual.** O teste mais recente relatado pelo proprietário é TEST14, não TEST11.

| Item | Resultado físico no Xbox 360 |
|---|---|
| Seletor e navegação/confirmar A | PASS |
| Textos do seletor centralizados conforme desejado | PASS — preservar alinhamento X=160 |
| Seletor permanece aberto por mais de 1 minuto, sem cutscene antes da confirmação | PASS |
| Slots vazios por idioma | PASS — NEW / NUEVO / NOVO |
| G/U sem cinza | FAIL — maiúsculas não resolveram |
| Prompt da attract/demo em English/Español | FAIL — a cutscene volta a mostrar APERTE START |

## Próxima etapa — candidata TEST15 preparada (ainda não testada no console)

1. **Prompt da attract/demo:** a PE mapeada exata da TEST14 foi recuperada e validada por SHA-256. A análise estática localizou uma chamada direta ainda nativa em `0x820DBEF8`, dentro de código executável. A TEST15 candidata redireciona essa chamada a um wrapper específico de prompt e remove o fallback para texto nativo que ocorria quando o ponteiro do controle era nulo. A hipótese faz sentido no fluxo analisado, mas só o teste no Xbox confirma se essa era a origem do prompt português.
2. **Candidata TEST15:** PE SHA-256 `d1657528056df5f8c1257f3197a2674f69a46ff14dd090b682bea47f4be4a8b4`; XEX SHA-256 `fcf76cbe7a5e8247341dd4215254eb8a759f989ab42700ccd305eaca09680cc1`; pacote ZIP SHA-256 `89a2f45e778afcb031d642f2f5820246a67b2584dfbc95874f4883f69454f121`. Round-trip XEX→PE conferido byte a byte; disassembly do wrapper revisada; testes sintéticos locais 5/5 PASS. Isso não equivale a validação no Xbox.
3. **G/U cinza:** segue FAIL/pêndencia. Não foi alterado o caminho de renderização do seletor, porque não há ainda uma causa confirmada. Maiúsculas já foram refutadas no teste físico.
4. **Teste físico pendente:** testar em pasta isolada; escolher English e verificar `PRESS START` quando entrar na attract/demo; reiniciar e repetir para Español com `PULSA START`. Preservar TEST14 e saves como rollback. O README dentro do pacote contém a sequência de teste.
5. **Regressões que devem permanecer PASS:** seletor centralizado em X=160, seletor ocioso sem cutscene antes do A, slots `NOVO/NUEVO/NEW`, base 30 FPS. Não declarar a correção da attract/demo até o teste físico.

Relatório técnico: [TEST15 — investigação do prompt da attract/demo](TEST15_PROMPT_DEMO_EN_ES_2026_10_20.md). O código do patcher e os testes sintéticos foram adicionados ao branch; [o workflow de CI passou (5/5 testes)](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39437813460).

Base preservada em 30 FPS; PT-BR mantido; Native60 e dublagem continuam fora de escopo nesta etapa.

---

# SM64 Xbox 360 — situação para o proprietário

**Atualização confirmada em 20/10/2026 — teste físico da TEST11 informado pelo proprietário.**

## Resultado do último teste no Xbox 360

O proprietário testou o pacote `SM64_TEST11_SELETOR_TRILINGUE_GLIFO_SEGURO_CANDIDATA_30FPS.zip` e relatou:

- O jogo abre normalmente e passa pela tela de créditos inicial.
- Chega à tela “APERTE START” com o seletor de idiomas.
- O direcional para cima/baixo percorre Português, Español e English.
- O botão A confirma a opção e avança para a etapa “APERTE START”, sem Fatal Crash relatado.
- **A seleção ainda não altera o idioma do jogo:** o texto continua “APERTE START” em português e não foi observada mudança para espanhol ou inglês.

**Conclusão:** a TEST11 está validada no hardware real para inicialização e navegação/confirmação do seletor, conforme relato do proprietário. A aplicação persistente do idioma continua sem funcionar/sem estar implementada de ponta a ponta. Não classificar como versão trilíngue concluída. O próximo trabalho deve rastrear o estado selecionado e ligá-lo às telas/textos posteriores (começando pelo “APERTE START” e, depois, menus de save), preservando a correção do cursor e a base 30 FPS.

**Pacote TEST11:** [ZIP candidato para teste](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/TEST9_TEST10_XENIA_CRASH_CAUSE_TEST11_2026_10_17.md). ZIP privado de 17.185.804 bytes; SHA-256 `175f8ab3dbb510827cde7d4156acd7f2f72c6beb482344a84ed2e813622d74d1`. O pacote não deve ser tratado como release final.

---

# SM64 Xbox 360 — situação para o proprietário

**Histórico anterior de 09/10/2026** (mantido abaixo como referência). Leia este arquivo para entender o progresso em 2 minutos; para trabalhar tecnicamente, comece por [PONTO_DE_RETOMADA.md](../PONTO_DE_RETOMADA.md), [AGENTS.md](../AGENTS.md) e [CHECKPOINT_PROJETO.md](../CHECKPOINT_PROJETO.md) **nesta branch**. Documento explicativo, não substitui os checkpoints.

[⬅ Painel central Xbox 360](https://github.com/PedroMarioaBros/OpenXeChain-X360-Builder/blob/main/docs/PAINEL_PMCN_XBOX360.md) · [Histórico e código](https://github.com/PedroMarioaBros/SM64toX360) · [GitHub Actions](https://github.com/PedroMarioaBros/SM64toX360/actions)

## Em uma frase
**O SM64 em PT-BR já existe e foi testado no seu Xbox; a edição com seleção Português/Español/English e dublagens ainda NÃO está pronta.** Esta frente faz patches e reconstrução de executável existente, não um build integral de fonte SM64 usando diretamente o OpenXeChain.

## Quadro do que existe

| Item | Situação que podemos afirmar |
| --- | --- |
| Base do jogo | Port Xbox 360 com base 30 FPS; PT-BR v0.4 é referência preservada. |
| Regressões conhecidas | `SELECTOR_TEST1` deu tela preta; `TITLE_SELECTOR_TEST1` causou regressão após estrela/retorno ao castelo. Não reutilizar patch rejeitado. |
| Progresso válido em hardware | RENDER90/TEXTO90 e versões de menu/saves em testes documentados; NOHOOK e PASSTHROUGH2 abriram, mas não validam seletor. |
| Seletor de idioma — TEST11 | **TESTADA NO XBOX FÍSICO em 20/10/2026 pelo proprietário:** jogo abre, passa pelos créditos, chega à tela de Start; direcional percorre Português/Español/English e A confirma sem crash relatado. **O idioma ainda não é aplicado ao restante da interface**: a tela continua “APERTE START” e não muda para espanhol/inglês. Candidata funcional para navegação, não release final. |
| Dublagem PT-BR | Patch BPS encontrado; VADPCM no patch e XEX analisados; falta associar vozes a amostras, codebooks e metadados reais. Nenhuma voz pronta foi extraída. |
| Dublagem ES | Pendente; não há integração validada. |
| Inglês original | Objetivo manter texto/vozes originais com comandos do Xbox; não confundir plano com entrega final. |
| Crawling em superfícies | Escopo definido e varreduras realizadas; mecânica ainda não implementada/testada no console. |
| Native60 | Histórico preservado; **fora do escopo** do produto atual 30 FPS. |
| Compilação na nuvem | CI de verificações estáticas, scripts de áudio e ferramenta xex2replace. **Não existe evidência de pipeline final automático para gerar e testar o SM64 trilíngue completo.** |

## Próxima ação técnica real
Conforme [auditoria VADPCM de 09/10](https://github.com/PedroMarioaBros/SM64toX360/blob/feature/multilang-dub-30fps/docs/PTBR_VADPCM_STRUCTURAL_AUDIT_2026_10_09.md): identificar referências/pointers e IDs de voz nos bancos 08/0A do PE Xbox e confirmar vínculo evento → sample → codebook → loop/tuning com dados autênticos. **Não gerar áudio por adivinhação nem anunciar WAV dublado antes de decodificar amostras reais.**

O problema do seletor é independente: retomar a rotina Press Start correta conforme checkpoints; não reutilizar o endereço de hook já rejeitado. A extensão de crawling continua no backlog.

## O que você NÃO precisa fazer agora
- Não instalar compilador no PC só porque o projeto tem testes CI.
- Não enviar novamente os mesmos checkpoints; estão registrados no GitHub.
- Não testar no console uma compilação que só passou em auditoria estática.
- Não abandonar a v0.4/PT-BR funcional para experimentar uma versão Native60.

## Como um novo chat/Work deve continuar
> Leia o HEAD de `feature/multilang-dub-30fps`, `AGENTS.md`, `PONTO_DE_RETOMADA.md` e `CHECKPOINT_PROJETO.md`. Preserve a base 30 FPS, PT-BR original, saves e versões aprovadas no Xbox. Continue da próxima evidência técnica pendente, registre resultados e commits no GitHub. Não invente XEX, vozes extraídas ou validação física.

**Pronto para seu Xbox somente quando:** pacote de teste real existir, com SHA-256 e roteiro claro; após teste físico, registrar boot, idioma, áudio, saves e regressões.

## Diagnóstico técnico mais recente — 20/10/2026

A leitura estática dos scripts identificou uma lacuna específica: o gate recebe a seleção e chama a rotina que troca os 170 ponteiros de diálogo, mas essa rotina não traduz por si só o prompt “APERTE START” nem os rótulos do menu de saves. Os testes de ativação existentes cobrem os ponteiros de diálogo, não esses textos da interface. Isso é coerente com o teste físico, mas ainda não é prova de falha na troca dos 170 diálogos.

Relatório técnico: [LANGUAGE_SELECTOR_ACTIVATION_GAP_2026_10_20.md](LANGUAGE_SELECTOR_ACTIVATION_GAP_2026_10_20.md).

**Trabalho desta etapa:** análise de código e documentação; nenhum PE/XEX foi modificado/gerado e nenhum teste novo de Xenia/hardware foi executado. Próximo passo é mapear os textos e rotinas reais no PE Xbox 360 usando bytes recuperados, antes de montar outra candidata.


## Complemento de teste físico — 20/10/2026 (relato do proprietário)

O proprietário acrescentou um resultado decisivo após testar a opção **English** na TEST11: selecionou English e confirmou com A; o prompt seguinte continuou “APERTE START” em português, mas **os textos dentro do jogo apareceram em inglês**. Isso demonstra que a escolha do idioma chega a pelo menos uma parte real do sistema de textos. O diagnóstico anterior deve ser refinado: não se pode concluir que a ativação dos idiomas falha por completo; a lacuna observada é que o prompt Press Start (e possivelmente outros elementos de título/file-select) não acompanha a escolha. Teste espanhol ainda pendente.

Não pedir novo teste de inglês. Aguardando apenas o resultado do teste espanhol que o proprietário já iniciou. Nenhum novo XEX foi gerado nesta atualização.


## Requisito confirmado para a próxima versão do seletor — 20/10/2026

O proprietário esclareceu o comportamento desejado para a tela do rosto do Mario: a ordem fixa deve ser **English → Español → Português**, com **English selecionado por padrão sempre que o jogo abrir**. A mudança de cursor deve atualizar imediatamente, antes de pressionar A, todos os textos do próprio seletor conforme o idioma destacado: título/etiqueta de idiomas, os nomes das três opções e a instrução de confirmação. Portanto, ao destacar English, todos esses textos ficam em inglês; ao destacar Español, ficam em espanhol; ao destacar Português, ficam em português. A confirmação com A seleciona o idioma para o jogo e seus textos internos. Não basta localizar somente a opção selecionada ou trocar textos depois da confirmação.

O proprietário está atualmente testando Español na TEST11; resultado ainda pendente. Este requisito é especificação nova, não implementação concluída. Nenhum novo XEX foi gerado nesta atualização.


## Esclarecimento da localização dos nomes das opções — 20/10/2026

O proprietário esclareceu que **os nomes das três opções também devem ser traduzidos conforme o idioma atualmente destacado**; não podem permanecer sempre como “English / Español / Português”. A ordem lógica continua fixa (primeiro inglês, depois espanhol, depois português), mas os rótulos visíveis mudam com o idioma ativo na prévia:

- **English destacado:** título “Languages”; opções “English”, “Spanish”, “Portuguese”; instrução “Press A to confirm”.
- **Español destacado:** título “Idiomas”; opções “Inglés”, “Español”, “Portugués”; instrução “Pulsa A para confirmar”.
- **Português destacado:** título “Idiomas”; opções “Inglês”, “Espanhol”, “Português”; instrução “Pressione A para confirmar”.

Toda a tela deve atualizar imediatamente ao mover o cursor, antes de pressionar A. Ao iniciar, English fica destacado por padrão. Este é um esclarecimento da especificação, não uma implementação concluída; não foi gerado novo XEX nesta atualização.


## Confirmação física do espanhol e escopo da próxima correção — 20/10/2026

O proprietário confirmou no Xbox 360 físico que os textos internos acompanham corretamente os três idiomas após selecionar e confirmar: Português → jogo em português; Español → jogo em espanhol; English → jogo em inglês. Portanto, a ativação do idioma para os textos internos está funcionando nos três idiomas segundo o teste relatado. Não pedir que repita esses testes.

Permanecem requisitos pendentes para a próxima versão:
1. Ordem visual fixa no seletor: English → Español → Português, com English selecionado por padrão ao abrir.
2. Prévia dinâmica antes de pressionar A: título, nomes das três opções e instrução de confirmação devem ser traduzidos para o idioma atualmente destacado. Exemplos: English = “Languages / English / Spanish / Portuguese / Press A to confirm”; Español = “Idiomas / Inglés / Español / Portugués / Pulsa A para confirmar”; Português = “Idiomas / Inglês / Espanhol / Português / Pressione A para confirmar”.
3. Após confirmar com A, o prompt/tela de “Press Start” precisa acompanhar o idioma selecionado, em vez de permanecer em “APERTE START”.
4. O menu de seleção de arquivos de save (file-select), incluindo os rótulos e instruções visíveis, também deve acompanhar o idioma selecionado.

Status técnico honesto: a tradução dos textos internos para os três idiomas foi confirmada pelo proprietário; o seletor dinâmico, o prompt Start e o file-select ainda não estão corrigidos/validados. Nenhum novo XEX foi gerado nesta atualização. Antes de editar o XEX, mapear as strings/rotinas reais no PE Xbox 360 e criar verificações estáticas seguras; não importar endereços N64/MIPS.


## Progresso técnico — mapeamento da PE TEST11, 20/10/2026

A PE mapeada da TEST11 foi recuperada do pacote da biblioteca e validada pelo SHA-256 registrado na auditoria: `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`. O wrapper real do seletor está em `0x823BCD00` (384 bytes; hash conhecido), e foi confirmado um cave auxiliar zerado em `0x823BCB00–0x823BCBFF`. Também foram mapeadas as strings reais do prompt Start e do menu de saves. Relatório: [mapa estático TEST11](TEST11_UI_TEXT_MAP_2026_10_20.md).

Os testes automatizados da variante `pregame_gate.py` passaram após implementar o padrão English e a troca de ponteiros da prévia dinâmica. **Limite importante:** essa é uma variante alternativa, não o wrapper físico TEST11; não contar isso como nova build nem como correção já visível no console. A próxima implementação deve ser aplicada ao wrapper TEST11 `0x823BCD00`, mantendo `.lang+0x80–0x87` intocado (scratch B/Y), e precisa testar a seleção dinâmica, prompt Start e strings do file-select. Nenhum novo XEX foi gerado.


## TEST12 — progresso real em código e testes, 20/10/2026

Foi criado `scripts/multilang/test12_live_ui.py` como patcher específico para a PE mapeada da TEST11, com hash de entrada fixado. Ele gera uma PE candidata de auditoria (hash `50fd4a1f07dcfccd232debfa48e656ac3618b2a3d6a676ca570c12888224ec30`), com wrapper de 564 bytes, auxiliar de menu de 108 bytes, English como padrão, prévia dinâmica, prompt Start localizado e 21 strings do menu de saves. A workflow de CPU [TEST12 Trilingual UI Static and CPU Tests](https://github.com/PedroMarioaBros/SM64toX360/actions/workflows/test-test12-live-ui.yml) passou, incluindo execução das instruções PPC do wrapper e auxiliar.

**Ainda não é uma build para o Xbox:** a PE candidata ainda não foi empacotada em XEX nem testada em Xenia/hardware. A prévia da fonte colorida usa transliterações sem acentos (INGLES/ESPANOL/PORTUGUES); a compatibilidade segura dos glifos acentuados ainda precisa ser resolvida antes de considerar a interface concluída. O scratch B/Y e o hook global foram verificados como preservados. Relatório: [TEST12 patch estático](TEST12_STATIC_PATCH_REPORT_2026_10_20.md).


## Correção TEST12 — ordem visual e acentos, 20/10/2026

A implementação foi refinada após comparar a ordem com o relato físico: no renderizador da tela, a coordenada maior corresponde à linha superior. Agora as linhas visuais são **English (topo) → Español (meio) → Português (baixo)**; o cursor começa em English (ID interno 2), DOWN percorre English → Español → Português e UP percorre o sentido inverso. As strings do seletor agora usam o renderizador nativo com mapa de glifos, incluindo os acentos solicitados. A workflow [TEST12 CPU](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39377225771) passou com 9 testes (4 estáticos + 5 PPC).

A PE candidata local mais recente tem SHA-256 `a71a6409b42de7e03db856654ba44540b462d3d71c5b650c6eb01c939ec6226b`. Ainda é PE mapeada, não XEX. O próximo passo é empacotar a XEX, fazer smoke test em Xenia e só então entregar para teste físico. Não pedir ao proprietário para testar um arquivo que ainda não foi gerado/validado.


## TEST12 — XEX empacotada e roundtrip verificado, 20/10/2026

O mapa de strings foi ampliado de 21 para **30 strings** de menu, pontuação e estado. A PE candidata atual tem SHA-256 `1a5ff2fad66879b207445ca0ab8bb480295eb8e52634756547506a58c4b9d4f8`. A XEX TEST12 foi empacotada com `xex2replace`, SHA-256 `d4a15796f13e9239aeba02cc446b0a0224ae9579b3af8e5564469454e2427d06`; a decriptação do payload e um segundo roundtrip reproduzem a PE exatamente.

A workflow [TEST12 CPU](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39378188850) passou em 9 testes (4 estáticos + 5 PPC). Um smoke test local do Xenia Canary Linux com renderizador nulo manteve TEST11 e TEST12 executando por 8 segundos sem fatal/exception. O renderizador nulo gera mensagens de falha de desenho e não valida a aparência visual; portanto, **ainda não é confirmação visual no Xenia**. O Xbox físico também ainda não foi testado com esta XEX.

Próxima etapa: empacotar o ZIP candidato para teste físico, com aviso claro de que a aparência do seletor, dos acentos e do menu de saves ainda precisa de confirmação visual. Preservar a TEST11 como rollback e não misturar 60 FPS.


## Pacote de teste TEST12 preparado, 20/10/2026

O pacote local de teste foi montado em `/mnt/data/SM64_TEST12_UI_TRILINGUE_CANDIDATA.zip` (SHA-256 `7eb04f6d65921bd002ae753ac3becbb08a3d8e97f72b5aed7f5c5fff6aade044`). Contém `default.xex`, instruções de teste, auditoria JSON e checksums. O XEX incluído tem SHA-256 `d4a15796f13e9239aeba02cc446b0a0224ae9579b3af8e5564469454e2427d06`. O pacote está rotulado como candidata, não versão final, pois o Xenia executado foi com renderizador nulo e não confirmou a aparência visual; falta a conferência no Xbox 360 físico.


## Resultado físico TEST12 — relato de 20/10/2026

O proprietário testou a XEX TEST12 no Xbox 360. A tela de créditos passa e o seletor chega à face do Mario; a ordem/estado das opções funciona (English, Español, Português), mas **nenhum texto do seletor é renderizado** — só aparece o marcador circular. Após confirmar, o prompt Start muda corretamente para o idioma escolhido; no menu de saves, o título e os demais rótulos parecem traduzidos, porém os quatro slots vazios continuam mostrando `NOVO` em PT-BR mesmo em English/Español.

Diagnóstico novo: o wrapper TEST12 chama `0x82143110` para desenhar os textos do seletor, enquanto o renderizador nativo já identificado e usado pelo código anterior é `PRINT_CENTER=0x8212B498`. Foi corrigida a chamada no código e atualizados os testes de runtime para exercitar o renderizador conhecido. Essa correção ainda precisa passar no CI e ser empacotada/testada; não existe nova XEX validada a partir dela neste momento.

Direção de UX sugerida: o proprietário gostou do seletor sem texto e propôs seta para a direita + bandeira de cada idioma (EUA, Espanha, Brasil). A proposta é boa e mais limpa; contudo, bandeiras exigem um caminho gráfico/sprite que ainda não foi provado no patcher. Próximo passo seguro: validar primeiro a correção do renderizador, investigar o texto `NOVO` nos slots e, em paralelo, auditar um método seguro para desenhar ícones/flags. Não presumir que o suporte a glifos de texto já permite desenhar bandeiras.


## Atualização técnica confirmada — 20/10/2026

O rótulo `NOVO` dos slots vazios foi localizado em um buffer de cinco bytes, sem espaço seguro para escrever `NUEVO`. A implementação agora redireciona o ponteiro para strings novas por idioma (`NOVO/NUEVO/NEW`) e usa uma pequena função PPC de 96 bytes em área de código livre. Os testes estáticos e os seis cenários PPC passaram no workflow [TEST12 Trilingual UI Static and CPU Tests](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39384550984); o [Multilang Static Check](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39384551048) também passou.

A tentativa de desenhar os cinco rótulos do seletor com `PRINT_CENTER=0x8212B498` foi revertida. Em um teste A/B no Xenia, esse caminho gerou crash guest em `0x8215F1A4`; a baseline TEST12 não mostrou o mesmo dump no ensaio de 14 segundos. Como o Xenia estava sem backend Vulkan funcional, isso não comprova a causa final nem valida o Xbox, mas a regressão é motivo suficiente para não entregar essa mudança. O seletor segue **sem rótulos visíveis**, como no teste físico TEST12.

Foi empacotada localmente uma variante exploratória que mantém o caminho antigo do seletor e corrige só `NOVO/NUEVO/NEW`. O roundtrip XEX→PE mapeada reproduziu exatamente a imagem, e o ensaio Xenia de 14 s não gerou dump de crash, mas o backend gráfico estava indisponível. Essa variante não é considerada build final nem foi validada visualmente no console.

Próxima etapa: auditar a pipeline gráfica para a seta e as bandeiras EUA/Espanha/Brasil, antes de gerar a próxima XEX física. Manter baseline de 30 FPS; Native60 e dublagem seguem fora do escopo.


## Atualização adicional — TEST13D (20/10/2026)

A investigação isolou uma provável incompatibilidade de terminador: a rotina de texto usada pelas cinco linhas do seletor é a função nativa de título `PRINT_CENTER=0x8212B498`, já comprovada nas TEST8/TEST9, e recebe strings ASCII terminadas por byte NUL. Os textos do seletor na TEST12 estavam codificados pelo mapa de glifos N64 e terminados em `0xFF`. A versão anterior que trocou o renderizador mantendo esse formato crashou no Xenia. Agora o código fonte mudou em conjunto: renderizador nativo de título + strings ASCII/NUL. Isso é uma hipótese técnica melhor fundamentada, não uma confirmação visual ainda.

- Última revisão em CI: commit `983aeeb4931fcc63593b3f5a0c4eb1424da3349d`; [TEST12 PPC runtime/static PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39386009924) e [Multilang Static Check PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39386009889).
- Empacotada uma **candidata experimental TEST13D** a partir da PE mapeada de TEST12 já testada no Xbox, corrigindo os strings do seletor para ASCII/NUL, retargetando apenas as cinco chamadas de desenho, e adicionando o ponteiro seguro `NOVO/NUEVO/NEW`.
- XEX `default.xex` SHA-256 `8f66a77718c033b409d85548fd456f48ec70999a824afa046555c4fc51d47524`; PE mapeada SHA-256 `0063a6dedb10b780c4e558f77af148bbf61bef0ae780f72647c112c2f44def9e`; AES decrypt roundtrip do payload da XEX reproduziu a PE byte a byte. ZIP CRC PASS.
- Xenia Canary Linux foi executado 16 s com TEST13D; processo terminou apenas pelo timeout solicitado (código 124), sem Access Violation nem KeBugCheck no intervalo. Entretanto, Xenia não inicializou Vulkan (`ErrorIncompatibleDriver`) e reportou falhas do backend PM4; então a etapa gráfica do preteste ficou **inconclusiva**, não PASS visual.
- A TEST13D está preparada somente para validar se as linhas passam a aparecer e se os slots vazios ficam `NEW/NUEVO/NOVO`. Os acentos dos rótulos estão provisoriamente sem acento por causa da fonte ASCII. A direção final aprovada segue sendo seta + bandeiras EUA/Espanha/Brasil; ela ainda não está implementada.

## Retorno físico TEST13D — seletor visível e slots trilíngues; refinamentos pendentes (20/10/2026)

O proprietário confirmou que, na TEST13D, o seletor aparece com título, três opções e instrução de confirmação na língua correspondente; navegação e seleção estão funcionando. Também confirmou que os slots vazios agora mostram **NOVO** em português, **NUEVO** em espanhol e **NEW** em inglês. Esses pontos passam a ser considerados confirmados em hardware, com base no relato recebido.

Novos problemas observados no console:
1. **Alinhamento:** todos os textos do seletor estão deslocados para a esquerda. Centralizar horizontalmente o título, os três nomes de idioma e a instrução de confirmação.
2. **Glifos cinza:** algumas letras (exemplos relatados: U e G) aparecem em cinza. Nenhuma letra do seletor pode ficar cinza; investigar o mapeamento/fonte e a rotina de renderização antes de escolher uma correção. Não presumir que trocar coordenadas resolve cor.
3. **Avanço automático para cutscenes:** se o seletor ficar ocioso, o jogo entra em cutscenes independentemente do idioma destacado. Evitar essa transição enquanto o seletor estiver aberto, sem quebrar navegação/seleção.
4. **Prompt localizado nas cutscenes:** ao entrar em cutscenes por inatividade e também depois de confirmar Español ou English, o prompt “APERTE START” aparece em português. Mapear todos os caminhos de renderização do prompt e fazer o idioma selecionado persistir também nessas telas.

Escopo seguinte: corrigir alinhamento, eliminar os glifos cinza, impedir a transição automática enquanto o seletor está ativo e localizar o prompt Start em todos os estados/cutscenes. Manter a base em 30 FPS, preservar TEST12 como rollback e não avançar para outros ajustes pontuais de idioma até esses comportamentos serem corrigidos e testados. TEST13D já confirma a visibilidade do seletor e os rótulos dos slots; não precisa pedir ao proprietário para repetir esses testes.

## TEST14 empacotada — 20/10/2026 (console ainda pendente)

Depois do relato físico da TEST13D, foi preparada a candidata TEST14 com centralização horizontal (X=160), rótulos do seletor em ASCII maiúsculo, reset do temporizador de demo enquanto o seletor aguarda A e redirecionamento da chamada alternativa de prompt em intro_game_over para o wrapper trilíngue. O helper de status dos slots foi deslocado para 0x823BCB70 sem sobrepor o helper de menu. A candidata conserva a base de 30 FPS.

**Integridade do pacote:** PE TEST14 SHA-256 6266c97deec43d4f43fe3c89bce2ebfb019ab220409702a35fccbd17b0878742; XEX SHA-256 a8f4aac287cafb7ddd68a2563284cc5583c9f318c4645704cab6d5cd6ccddbcb; ZIP SHA-256 706603e38aa12ae34868eab327b6073cb6881628179507e444f2fafa0fafc858. ZIP verificado e roundtrip XEX→PE reproduziu bytes idênticos.

Os workflows do código passaram:
- [TEST12 Trilingual UI Static and CPU Tests — run 39423432009](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39423432009)
- [Multilang Static Check — run 39423432106](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39423432106)

**Não marcar como corrigido ainda:** centralização, ausência de glifos cinza, manutenção do seletor sem cutscene até A e prompt localizado em demos/cutscenes exigem confirmação física em TEST14. Não foi reivindicado PASS visual/Xbox desta candidata.

Pacote de teste: `SM64_TEST14_CENTER_SELECTOR_IDLE_DEMO_START_PROMPT_30FPS.zip`, disponibilizado nesta conversa. Roteiro completo e hashes: [relatório TEST14](TEST14_CENTRAL_SELECTOR_IDLE_DEMO_START_PROMPT_2026_10_20.md).

## Retorno físico TEST14 e correção de escopo do prompt — 20/10/2026

O proprietário confirmou no Xbox:
- Seletor ocioso por mais de 1 minuto sem cutscene: **PASS**.
- Slots vazios NEW / NUEVO / NOVO: **PASS**.
- Letras G e U ainda cinza mesmo em maiúsculas: **FAIL**; a hipótese de que bastava trocar caixa foi refutada.
- Depois de escolher English/Español, a tela inicial mostra o prompt no idioma certo, mas o attract/cutscene volta a mostrar APERTE START: **FAIL**.

Diagnóstico com base no registro TEST7: a TEST14 só redirecionava `intro_game_over` em `0x82147368`; o caminho `intro_regular` em `0x821472D4` continuava intacto e é um candidato forte para o prompt que aparece durante o attract/demo. O patcher agora inclui hook para o callsite regular além do hook de Game Over. Os testes automatizados precisam confirmar essa mudança antes de produzir outro XEX.

Não declarar os problemas concluídos: o bloqueio de idle e os slots estão confirmados; G/U cinza e prompt em cutscenes permanecem pendentes. O próximo trabalho é validar o hook de `intro_regular` e investigar a fonte/paleta/mapeamento dos glifos em vez de repetir apenas a troca para maiúsculas. TEST12 e TEST13D preservadas como rollback; 30 FPS, sem Native60 nem dublagem.

### Retificação técnica importante — caminho da cutscene

A auditoria do patcher mostrou que o callsite `0x821472D4` de `intro_regular` já está redirecionado ao wrapper do seletor na TEST14 (`48275a2d` → `0x823BCD00)); portanto, não ficou intacto e não deve receber um segundo hook. A tentativa de duplicar esse hook foi removida antes de qualquer nova XEX. O hook adicional em `0x82147368` não resolveu o prompt observado no attract/cutscene. O caminho real ainda precisa ser isolado entre os demais chamadores de `print_intro_text` (VA `0x82098D18`) e o estado usado no demo.

Os testes automatizados voltaram a passar após remover a hipótese duplicada: [TEST12 UI tests — run 39427028860 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39427028860). Isso não é confirmação física nem correção do prompt.


## Complemento do retorno físico TEST14 — 20/10/2026

**Centralização confirmada pelo proprietário:** os textos do seletor ficaram centralizados exatamente como desejado. Marcar como PASS no Xbox; não é mais pendência. Também estão confirmados o bloqueio de cutscene enquanto o seletor fica aberto por mais de um minuto e os slots NEW/NUEVO/NOVO. G/U permanecem cinza mesmo em maiúsculas; e o attract/demo mostra APERTE START depois de selecionar English/Español. Próximo diagnóstico: enumerar, a partir da PE mapeada TEST14, outros chamadores de `print_intro_text` (VA `0x82098D18`) e rastrear o estado de idioma no demo; investigar a rotina/índice de glifos para G/U. Ainda não foi encontrada a causa final nem gerado XEX novo. Não declarar correção até teste físico.


## Ferramenta técnica preparada nesta retomada (20/10/2026)

Foi adicionado um scanner somente leitura para procurar candidatos de chamadas PPC a print_intro_text na PE mapeada, com testes sintéticos. CI dos testes do scanner e validação de fontes passaram: [scanner-tests](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39430369587) e [validate-sources](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39430369450). **Ainda não foi executado na PE real TEST14**, pois o pacote ZIP contém somente default.xex, README e auditoria; nenhum chamador novo foi identificado e nenhuma XEX nova foi gerada.
