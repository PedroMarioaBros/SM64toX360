# TEST10 no Xbox: Fatal Crash ao pressionar UP, DOWN ou A — 17/10/2026

## Resultado do teste em hardware — fonte: proprietário
A TEST10 `SM64_TEST10_DIAGNOSTICO_LEITURA_CONTROLES_30FPS.zip` abriu o jogo, passou pelos créditos e chegou à tela de abertura com a lista de idiomas. O usuário testou três vezes, com reinicializações:
1. **D-pad UP**: Fatal Crash;
2. **D-pad DOWN**: Fatal Crash;
3. **Botão A**: Fatal Crash.

O analógico direito não provocou resposta visível, o que é esperado: a TEST10 não implementa leitura dele. **Não houve seleção de idioma, acesso a save ou teste de estrela→castelo.**

**Classificação: TEST10 FAIL HARDWARE_FATAL_CRASH_ON_RECOGNIZED_INPUT; NÃO REEXECUTAR.**

A TEST9 já havia falhado ao entrar na tela de escolha. A TEST8 é a última tela de idiomas visualmente aprovada no Xbox, e a TEST3 segue a única versão com estrela→castelo comprovadamente aprovado.

## Investigação de caminho real — mudança de hipótese importante

A denominação anterior “somente leitura de controles” era incompleta: a TEST10 lê o controle, **mas também acrescenta uma quinta chamada de renderização** para imprimir a letra `X` caso UP/DOWN/A estejam pressionados.

Desmontei/inspecionei a sequência real de **204 bytes PowerPC** extraída do PE TEST10, SHA-256 `4fd27ff93e2ed0140a849e971b0a9bcdcd39f0b86665506f0af8c78a956b4a6f`:

| Endereço VA | Instrução PPC | Função |
|---|---|---|
| `0x823BCD0C` | `bl 0x82098D18` | Título original |
| `0x823BCD20`, `0x823BCD34`, `0x823BCD48`, `0x823BCD5C` | `bl 0x8212B498` | Desenha os quatro títulos fixos |
| `0x823BCD64` | `lwz r11,-30320(r11)` | Consulta endereço global do controle |
| `0x823BCD70` | `lhz r9,16(r11)` | Lê `buttonDown` (quando ponteiro não nulo) |
| `0x823BCD74`, `0x823BCD88`, `0x823BCD9C` | `andi.` | Reconhece UP, DOWN, A respectivamente |
| **`0x823BCDB8`** | **`bl 0x8212B498`** | **Nova quinta chamada de desenho, somente com tecla reconhecida, imprime `X`** |

- O PE TEST10 efetivamente contém `X\0` no VA `0x8305CA24`, apontado pelo código; não foi detectada string sem terminador.
- Não existe store na estrutura do controle em nenhum dos 204 bytes. O código **não escreve em `buttonPressed` ou `buttonDown`**.
- O arquivo TEST10 realmente contém as condições para UP/DOWN/A e chama a mesma função gráfica da TEST8, mas em **uma chamada adicional por quadro quando detecta esses botões**.
- O emulador PPC32 passa esses caminhos e não reproduz o crash real. O Unicorn PPC64 anterior falhou antes da primeira instrução e é inconclusivo.

**Conclusão técnica mais estreita:** a combinação de três ações distintas que causam o mesmo Fatal Crash aponta para o caminho que elas compartilham após o teste de bits. O caminho compartilhado é a nova chamada `print_text_centered("X")`. O motivo do crash nesse caminho **não foi determinado**: pode envolver o contexto da chamada, o número de itens no renderizador, instruções/estado PPC64 ou alocação gráfica. Os fatos NÃO demonstram que ler `buttonDown` seja a causa, nem que a quinta chamada isoladamente seja defeituosa.

### Testes estáticos novos
`scripts/multilang/test_test10_postmortem_paths.py` valida sem distribuir PE/XEX:
- Exatamente o código de 204 bytes da TEST10 (SHA fixado);
- Quatro chamadas de impressão incondicionais e quinta condicional no final;
- Bits `0x0800` (UP), `0x0400` (DOWN) e `0x8000` (A);
- Ausência de qualquer escrita na estrutura do controle;
- Endereço da string `X` e assinatura de instrução.

**São verificações binárias, não testes de gameplay nem reprodução do crash.**

## Próximo plano — sem solicitar outro Fatal Crash por tentativa e erro

1. **Suspender TEST9 e TEST10**; não pedir qualquer nova execução. Preservar TEST3 e TEST8 intactas.
2. Estudar a implementação de `print_text_centered` e seu gerenciamento de fila/memória, especialmente diferenças entre as 4 chamadas estáticas aprovadas na TEST8 e a quinta chamada condicional da TEST10. A referência decompilada expõe `sTextLabels[52]`, então **não afirmar sem prova que há limite de 4 ou 5 textos**, embora o pool de efeitos em runtime ainda exija atenção.
3. Revisar todos os caminhos/retornos PPC64 e invariantes ABI da nova chamada, sem confiar só na emulação PPC32.
4. **Próximo desenho de teste, somente após análise:** manter **exatamente quatro chamadas de desenho por quadro** e usar o input para escolher o texto em um dos slots existentes, sem uma quinta chamada; preservar temporariamente Start, memória de controle e gameplay. Esse teste separará reconhecimento de botão de adição de chamada gráfica, se for justificado e verificado antes do hardware.
5. Somente depois de conseguir input sem crashes, implementar estado de seleção e confirmação, e depois ativar tabelas PT/ES/EN. A dublagem está integralmente fora do escopo por ordem do proprietário.

**Não há TEST11 disponível, correção definitiva ou novo XEX aprovado neste diagnóstico.** Não inventar porcentagem de conclusão.
