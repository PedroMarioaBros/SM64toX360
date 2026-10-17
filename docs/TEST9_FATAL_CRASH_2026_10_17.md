# TEST9: FATAL CRASH NA TELA DE SELEÇÃO — 17/10/2026

## Resultado de hardware REAL, informado pelo proprietário

**TEST9 REPROVADA (FATAL CRASH)**: o jogo abre normalmente, passa pelos créditos iniciais e sofre **Fatal Crash ao chegar à tela em que deveria aparecer a seleção de idiomas**, antes de haver qualquer confirmação de idioma relatada. O usuário não informou resultados de navegação, ativação, save ou retorno de estrela, pois o crash impediu os testes.

**Não pedir nova execução da TEST9. Não declarar seletor funcionando. Não interpretar oito testes Unicorn PASS como validação em hardware.**

### Ponto de controle comprovado

A TEST8 anterior **PASSOU no Xbox** e exibiu quatro linhas coloridas `IDIOMAS TESTE8 / PORTUGUES / ESPANOL / ENGLISH`, conforme fotografias enviadas pelo proprietário. A TEST8 apenas desenhava a lista; não lia botões nem ativava tabelas. Portanto, o callback gráfico em `0x821472D4` e `print_text_centered` são utilizáveis em hardware **com o código da TEST8**, não necessariamente com todas as alterações da TEST9.

Última base funcional de *gameplay* com teste estrela→castelo continua sendo a TEST3. Não confundir a estabilidade da TEST8 somente na tela de título com teste completo de gameplay.

### Inspeção binária local real da TEST8 → TEST9

Os dois XEX foram efetivamente convertidos às imagens PE para inspeção (artefatos privados). Diferenças mapeadas:

- TEST8 PE SHA-256: `fab6a7c31d1fa2cb4aea3ad5e0f3171bde5248a13f48bbcab56d2bc05fc4c438`.
- TEST9 PE SHA-256: `a405ba6e97c933298a1e24361423b7230f75957a4ee0c0ecfced21d957b2e641`.
- **343 bytes efetivamente diferentes**, confinados a: substituição do wrapper em `0x3BCD00..` (112 → 384 bytes); duas strings `TESTE8`→`APERTE`; cursor e apêndice de textos ASCII na seção `.lang`.
- **CALLSITE de título `0x1472D4` IGUAL** nos dois: `48275a2d`; despacho original `0x147448` IGUAL `4bfffe31`; execução global de scripts `0xCD128` IGUAL `4bfc8321`.
- Os 170 ponteiros dos diálogos e os dados de nomes de fases/estrelas permanecem idênticos; `.lang+0x14` e `+0x18` ainda inicializam a zero.
- O valor estático em `0x823C8990` aponta para `0x82E47BB8`. O código **nativo** de `intro_regular` usa `lis r11,0x823D; lwz r11,-30320(r11); lhz r10,18(r11)` para ler o campo buttonPressed, um acesso de leitura presente no executável original.
- O wrapper TEST9 introduz **acesso anterior ao controle e escrita ativa via `sth r8,18(r11)`**, mascarando Start antes da verificação nativa. TEST8 não executa essa escrita. Há também novas ramificações para DPAD/A e novos rótulos nativos. Esses elementos constituem os principais diferenciais de execução; **não é possível identificar o culpado exato apenas pelo crash observado**.
- A leitura de rótulos ASCII em `.lang` já funcionou na TEST8. Seis chamadas coloridas de render por quadro na TEST9 versus duas do título mais quatro do overlay TEST8 não indicam, por si, estouro da fila de 52 rótulos nativa, mas ainda é necessário verificar o estado de render em hardware.
- O wrapper TEST9 de 384 bytes cabe na mesma página executável usada pelo wrapper de 112 bytes da TEST8; esta verificação de faixa não garante ausência de conflito de runtime.
- `source`: `scripts/multilang/test9_selector_native.py`; 5 testes de PPC Unicorn 32-bit + 3 de reprodutibilidade [PASS 39010452532](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39010452532), mas estes **não modelaram fielmente inicialização real nem a semântica completa da ABI PowerPC64 do Xbox**, nem hardware gráfico real.

### Hipótese, não diagnóstico definitivo

A suspeita prioritária é a **alteração prematura e direta de `buttonPressed` na estrutura do controle**, executada imediatamente no primeiro quadro do callback da intro, combinada à ausência de observação em CPU Xbox. Também precisam ser eliminados acesso a estado, escrita nos ponteiros somente após A e dependências de render. **Nenhuma dessas hipóteses foi demonstrada individualmente**.

### Próxima ação de engenharia

1. **Retirar TEST9 de qualquer categoria de versão funcional e suspender novos testes dessa XEX**. Não retestar Fatal Crash.
2. Voltar à TEST8 para todos os experimentos sobre intro, pois foi **a última exibição visual aprovada no console**; preservar a TEST3 como referência de gameplay/estrela.
3. Separar **leitura do controle**, **desenho do marcador**, **bloqueio de Start** e **cópia dos ponteiros** em testes independentes, com guardas de memória/endereço, antes de reunificá-los. Não alterar controller->buttonPressed prematuramente; preferir gate de Start no controle nativo de fluxo de intro, sem modificar sua estrutura global.
4. Testar rotinas em contexto PowerPC64 quando houver ferramenta válida; `UC_MODE_32` isolado não é prova suficiente. **Não gerar TEST10 aleatória ou anunciar solução antes de isolar o ponto problemático.**
5. Checar integridade PE/XEX e espaço livre de código para quaisquer candidatos. Em hardware, **somente testes limitados** após análise, e parar no primeiro crash.
6. Não modificar a tradução portuguesa ou trabalho de vozes. **Dublagem totalmente fora do escopo até três idiomas e seletor funcionando e aprovados no Xbox**.

O diagnóstico exato do Fatal Crash **continua aberto**. Não inventar explicação conclusiva nem percentuais de conclusão.


## Verificação adicional PPC64 — importante não interpretar falsamente

Para compreender o limite dos cinco testes CPU32 PASS, foi criado `scripts/multilang/probe_test9_ppc64_mode.py` (workflow `test9-ppc64-abi-probe.yml`). A tentativa de emular o primeiro quadro da TEST9 sob `UC_MODE_64 | UC_MODE_BIG_ENDIAN` em Unicorn 2.1.4 levantou `UC_ERR_EXCEPTION`, errno 21, **antes da execução de qualquer instrução** (`executed_count=0`, `last_instructions=[]`). Resultado classificado como **INCONCLUSIVE_UNICORN_PPC64_ABORTED_BEFORE_FIRST_INSTRUCTION** (backend indisponível/inadequado nessa configuração), **NÃO como reprodução do Fatal Crash no Xbox**.

- [CI de diagnóstico de capacidade PPC64, run 39011849760](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39011849760) — probe completado; PPC64 não executou instruções.
- O suporte de TEST9 continua limitado aos 5 testes sintéticos PPC32 e validação estática/XEX. Nenhum teste de CPU64 com execução real pode ser reivindicado.
- Ponto exato e causa do Fatal Crash em hardware permanecem **não identificados**. A próxima investigação deve comparar variantes mínimas (controller read / START mutation / render) com segurança, preferir não escrever no buffer global de botão, e preservar TEST8 aprovada visualmente.
