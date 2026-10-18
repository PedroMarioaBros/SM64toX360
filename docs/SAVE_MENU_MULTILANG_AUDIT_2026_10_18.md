# Auditoria do menu de saves multilíngue — 18/10/2026

## Resultado desta retomada

Esta é uma auditoria estática dos arquivos-fonte disponíveis na branch `feature/multilang-dub-30fps`; não é um teste novo do Xenia nem do Xbox físico.

O relatório de TEST11 de 17/10 já comprova o seguinte no Xenia Canary Linux (XEX privado executado localmente): o seletor aceita PT/ES/EN, confirma a escolha, bloqueia Start antes da confirmação e entra no fluxo de saves sem crash dump. Porém, depois de escolher Español, o menu de saves continua em português (`ABRIR JOGO`, `PTS.`, `COP.`, `APAGA`, `ESTEREO`). O jogo dentro da fase, salvamento e retorno ao castelo ainda não foram validados nessa candidata.

## O que o código atual cobre

A leitura de `scripts/multilang/build_lang_section.py` confirma que a seção `.lang` contém:
- três pools de texto de diálogo, PT-BR/ES/EN;
- 170 entradas por idioma;
- textos do seletor e dos créditos;
- tabelas de ponteiros para as entradas de diálogo.

A leitura de `scripts/multilang/language_activation.py` confirma que a rotina de ativação copia somente os ponteiros dos 170 diálogos para os registros nativos do jogo, com stride de 16 bytes. Ela não troca uma tabela geral de textos da interface.

**Conclusão delimitada:** o menu de saves não está coberto pelo mecanismo de troca dos 170 diálogos. Isso explica por que a seleção de idioma funciona e a interface de saves permanece em PT-BR, sem provar ainda onde cada rótulo está armazenado nem qual é a forma mais segura de alterá-lo.

## Próxima investigação necessária

1. Usar o PE mapeado exato da candidata TEST11 e procurar as referências de texto/renderização dos rótulos nativos do menu de saves: `ABRIR JOGO`, `PTS.`, `COP.`, `APAGA`, `ESTEREO`.
2. Determinar se cada rótulo é uma string fixa, um token do charmap ou texto montado por código; registrar VA, offset no PE, bytes originais e referências cruzadas.
3. Identificar o ponto em que o idioma selecionado está disponível para a rotina do menu, sem alterar o hook de gameplay, o fluxo de saves ou a tabela de diálogos já validada.
4. Criar primeiro uma auditoria reproduzível e testes estáticos fail-closed. Não preparar XEX por adivinhação nem declarar que os rótulos foram localizados até registrar evidência binária real.
5. Depois de construir uma candidata, executar no Xenia Linux com bindings confirmados: entrar no menu de saves em cada idioma; iniciar fase; verificar textos; coletar estrela; voltar ao castelo; testar persistência dos saves. Xenia PASS não substitui validação física.

## Guardrails preservados

- Base de produto: 30 FPS; não misturar Native60.
- Preservar o PT-BR canônico, os controles Xbox 360 e as regressões já documentadas.
- TEST11 segue como candidata aprovada apenas no escopo documentado do Xenia; hardware físico pendente.
- Dublagem permanece fora de escopo até a experiência trilíngue textual estar estável e haver nova autorização explícita.
- Nenhum PE/XEX, ROM ou áudio proprietário foi adicionado ao repositório público.

## Arquivos inspecionados

- `docs/TEST9_TEST10_XENIA_CRASH_CAUSE_TEST11_2026_10_17.md`
- `scripts/multilang/build_lang_section.py`
- `scripts/multilang/language_activation.py`
- `PONTO_DE_RETOMADA.md`
- `AGENTS.md`

Este registro documenta o ponto técnico concreto para continuar sem repetir os testes de cursor já concluídos.
