# TEST6 em Xbox 360 — marcador visual confirmado (17/10/2026)

## Evidência do teste do usuário

Duas fotografias da TV foram enviadas após o teste da TEST6. A primeira mostra a cabeça do Mario contra o cenário repetido de Super Mario 64; a segunda mostra claramente o texto **TESTE6 START** na tela original de título, sem exibir Português / Español / English.

**Resultado inequívoco: TEST6 = PASS no marcador visual. Seletor de idiomas = FAIL / continua não funcional.**

Isso comprova que o console está executando um pacote com pelo menos os recursos de tela modificados da TEST6. **Não comprova que a rotina PowerPC do seletor está rodando**, nem prova por si só que todo o XEX foi executado conforme esperado. Não atribuir essa falha a uma versão antiga no dispositivo, pois o próprio texto modificado apareceu.

## Achado de arquitetura por fonte e PE real

No código original SM64 fixado:
- `src/game/area.c:print_intro_text()` desenha o texto "PRESS"/"START", usando `print_text_centered`. Este é o mesmo recurso do texto TESTE6 START, comprovadamente visível no console.
- `src/menu/title_screen.c:intro_regular()` chama `print_intro_text()` **antes** de avaliar o Start.
- `src/menu/title_screen.c:intro_game_over()` também chama `print_intro_text()` **antes** do Start.
- `src/game/level_update.c:play_mode_normal()` chama `print_intro_text()` nos demos; por isso não interceptar irrestritamente a função global de impressão sem condicionamento de estado de tela.

No PE TEST6 (base `0x82000000`):
- `print_intro_text` VA `0x82098D18` (endereço existente e executável); contém duas chamadas para **`print_text_centered` VA `0x8212B498`**, a mesma rotina gráfica por trás da palavra TESTE6.
- `intro_regular` chama `print_intro_text` pela BL em **`0x821472D4`**, opcode `4bf51a45`.
- `intro_game_over` chama `print_intro_text` pela BL em **`0x82147368`**, opcode `4bf519b1`.
- `lvl_intro_update` alterna entre `intro_regular` e `intro_game_over`, conforme argumento de Level Script.
- O script da intro tem comandos `CALL_LOOP` com argumento 1 em região mapeada `0x7FBA4C` para a função `lvl_intro_update` em `0x82147408`; mesmo assim a execução no Xbox NÃO foi observada diretamente.
- Na TEST5/TEST6 há patch de BL em `0x82147448` que aponta a `0x823BC900`. Se ele rodasse no estado estático original 0, Start seria impedido de avançar. Mas o Start avançou; isso coloca em questão o caminho dinâmico efetivamente chamado ou o estado alterado em runtime. Só disassembly não resolve essa contradição.
- **A rotina PRINT antiga `0x82143110` não é a mesma que desenha o título nativo `0x8212B498`**. Não confundir as fontes/tabelas de glifos usadas por essa renderização.

## O que agora está comprovado e o que ainda não está

- TEST3: funcional no Xbox ao pegar estrela e retornar ao castelo (histórico aprovado).
- TEST4: boot/saves/jogo PT PASS, seletor FAIL.
- TEST5: boot/saves/jogo PT PASS, seletor FAIL.
- TEST6: **marker TESTE6 START aparece no Xbox**, screenshot comprova; seletor continua ausente. Sem teste de estrela→castelo nesta build.
- **Nenhum teste comprova chamada de código do seletor durante título em hardware**; não repetir cópia dos mesmos hooks apenas porque houve CPU Unicorn PASS.

## Próxima implementação a preparar

1. Fazer diagnóstico/integração **restrita às chamadas de `print_intro_text` dentro de `intro_regular` e `intro_game_over`**. São locais concretos associados ao recurso já observado na TV, e a edição de ambas as chamadas evita supor que só o `LVL_INTRO_REGULAR` roda.
2. Se for necessário substituir a renderização, usar **`print_text_centered` VA `0x8212B498`**, originalmente usado no título, e strings no formato aceito por esta função; as strings de diálogo codificadas pelo N64 possuem encoding distinto e não podem ser presumidas compatíveis com o título.
3. Na fase diagnóstica, isolar PRIMEIRO que o novo desenho é visível e a rotina roda no hardware, sem instalar troca de idioma/saves. Só depois ligar D-pad/A e as tabelas de 170 diálogos + 26 cursos/90 estrelas, preservando o jogo original.
4. Não reeditar o hook global de `level_script_execute` que causou crash no retorno das estrelas. Não mexer nos controles B/Y. Não avançar para dublagem.
5. Uma futura build deve preservar a TEST3 original e o fallback, e ter testes dirigidos à renderização nativa do título além da emulação CPU isolada.

**ATENÇÃO: este documento é investigação comprovada/planejamento técnico; NÃO existe um TEST7 preparado/entregue. A TEST6 foi diagnóstica, não uma correção de idioma.**
