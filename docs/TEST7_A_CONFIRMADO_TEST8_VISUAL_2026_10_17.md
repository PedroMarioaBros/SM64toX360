# TEST7 hardware A → TEST8 sobre a renderização nativa do título (17/10/2026)

## Dado comprovado no Xbox 360
O proprietário informou **opção A na TEST7**: o rosto do Mario apareceu, mas a mensagem **TESTE7 START não apareceu** (durante a janela de observação). Isso confirma que a chamada `intro_regular → print_intro_text` no offset PE mapeado `0x1472D4` participa do desenho da abertura. **Não conclui que o antigo wrapper seletor da TEST5 executou corretamente**, nem aprova os três idiomas.

- TEST3: base aprovada com estrela→castelo.
- TEST4, TEST5: abriram, mas seletor não apareceu.
- TEST6: mostrou marcador TESTE6 START na TV.
- TEST7: rosto do Mario sem TESTE7 START (hardware **A**); portanto a chamada de impressão em intro_regular foi de fato observada por diferença negativa.

## Nova direção: mesma função gráfica comprovada
O binário real TEST7 e o fonte fixado `n64decomp/sm64/src/game/print.c` mostram `print_text_centered(s32 x,s32 y,const char* text)`, VA `0x8212B498`, consumindo **ASCII encerrado em byte zero**, ao contrário dos textos de diálogo N64 encerrados por `0xFF`. O título real chama esse renderizador por `print_intro_text`, VA `0x82098D18`.

A versão TEST5 tentava desenhar as opções usando outra rotina `0x82143110` e textos de outra codificação. Pode ser parte da causa do seletor invisível, mas **não há prova conclusiva** sem a execução de visualização.

## TEST8 — VISUAL, NÃO SELECIONÁVEL

XEX Basic reconstruído usando como fonte **a TEST7 exata**. A TEST8 restaura o desvio no dispatcher `lvl_intro_update` que havia falhado, e substitui somente a BL de impressão em `intro_regular` por uma BL para wrapper PPC curto, cuja execução espera observar pela tela. Essa rotina:

1. chama primeiro a função de título original `print_intro_text`;
2. chama `print_text_centered` original quatro vezes para apresentar `IDIOMAS TESTE8`, `PORTUGUES`, `ESPANOL`, `ENGLISH` em posições à esquerda do Mario;
3. restaura LR/stack e retorna à lógica original de Start e saves.

**Acentos e iniciais minúsculas são provisórios no teste visual**, pois a meta atual é comprovar renderização da lista com o alfabeto nativo do título. **TEST8 NÃO processa input nem ativa novo idioma.** Não indicar que a lista é interativa.

### Binário e hashes
- ZIP: `SM64_TEST8_VISUAL_IDIOMAS_30FPS.zip`, SHA-256 **`5fbd56533f6c211d6ef87785cf83eb047dcb77d2a669805e7a5c1158e4d7e4a7`**, 17.184.919 bytes, CRC PASS.
- `default.xex` SHA-256 **`006b662635b41f8a0e2996a8fbba43ab354acdca11ed21c184e6bf669daa1ccb`**, 17.182.720 bytes;
- Imagem PE TEST8 SHA-256 **`fab6a7c31d1fa2cb4aea3ad5e0f3171bde5248a13f48bbcab56d2bc05fc4c438`** (17.170.432 bytes);
- Base PE TEST7 SHA-256 `cee2a0cbb4bbb7b47e867e387b13f81e71e72a2f60134851abedc9bfbd4986aa`; hash bloqueado no script;
- **Roundtrip exato XEX2 Basic AES→PE PASS**, reconstrução com utilitário host xex2replace;
- Wrapper proposto em **`0x823BCD00`**, cave reservada `0x200` **verificada toda zero** na TEST7; rotina de **112 bytes**, SHA `53fcb898120d7b30526770bf1e58b622f87aa582b519ef8d9d001251c2991d5c`.
- A primeira proposta de cave `0x823BCF00` **foi rejeitada** pela guarda de bytes livres pois colidia com código existente em `0x823BD000`. A montagem abortou e foi reiniciada em endereço comprovadamente vazio `0x823BCD00`.
- Tabelas originais de 170 diálogos, nomes PT-BR/ES/EN, controles B/Y, scripts globais, saves e áudio não alterados. O desvio antigo TEST5 `0x82147448` foi restaurado para `4bfffe31`. A chamada `0x821472D4` da intro é direcionada para o wrapper, que chama o desenho original e renderiza os rótulos.
- Texto ASCII adicionado somente no espaço livre da seção `.lang` já existente (45 bytes de cursor consumidos), sem sobrescrever qualquer pool PT-BR; metadados de cursor atualizados.
- Diferenças binárias do PE permitidas: bloco novo de 112 bytes, duas BLs de intro/dispatcher, duas strings marcador TESTE7→TESTE8, cursor `.lang`, quatro strings ASCII anexadas. **148 bytes efetivamente diferentes** do PE anterior, confinados às regiões auditadas.

### Regressões
- [GitHub Actions TEST8 Native Intro Visual Audit — 39008801116](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39008801116): **5 testes PASS**, sem conter XEX/ROM proprietário. Verificam entradas ASCII nulas, hash do código, cave vazia, chamada correta, rollback do antigo hook e preservação do PT-BR, B/Y e scripts.
- Código reproduzível em `scripts/multilang/test8_native_title_visual.py`. Executável XEX foi construído em ambiente privado com a imagem fornecida pelo proprietário.
- Backup privado: Library `/Xbox360 - SM64 PTBR/SM64_TEST8_VISUAL_IDIOMAS_30FPS.zip`, id `libfile_9e708b07a3248191bfda3be2e3c6a211`. **Não distribuir publicamente no GitHub**.

## O que Pedro deve observar

Executar TEST8 em **pasta separada** mantendo TEST3 e saves intocados. Na tela de título com rosto de Mario, aguardar alguns segundos.

- Apareceu o título `IDIOMAS TESTE8` mais `PORTUGUES/ESPANOL/ENGLISH`: demonstra renderização de múltiplos textos por novo código no ponto comprovado de intro; próximo estágio será implementar D-pad/A e ativação real das tabelas.
- Apareceu só `TESTE8 START` (sem quatro linhas): prova marcador de texto atualizado, porém a rotina adicional ainda não apresentou o overlay; investigar chamada/execução ou limites de renderização antes de nova versão.
- Crash/tela preta: interromper, manter TEST3 original e reavaliar contexto gráfico do wrapper.

**Não é uma nova versão multilíngue funcional**. Não precisa jogar fase ou carregar save para essa etapa. Não retomar dublagem; ela está proibida até três idiomas, tela de escolha e jogo completo aprovados no Xbox 360 e nova autorização explícita.
