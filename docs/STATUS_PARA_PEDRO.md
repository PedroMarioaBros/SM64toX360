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
