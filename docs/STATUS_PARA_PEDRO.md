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
