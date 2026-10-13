# TEST4 sem seletor → TEST5 com chamada do título corrigida — 13/10/2026

## Resultado REAL reportado pelo proprietário para TEST4

No Xbox 360 real, a TEST4 `SM64_TEST4_SELETOR_TRILINGUE_30FPS_TESTE_XBOX.zip`:

- abriu normalmente, exibiu os créditos iniciais;
- exibiu a tela habitual de **Aperte Start**, **SEM qualquer seletor de idiomas**;
- entrou no menu de saves, carregou um arquivo e iniciou jogo em **português**;
- NÃO confirmou tradução EN/ES, seleção nem retorno após pegar estrela nesta build.
- Classificação: **boot/menu/PT-BR parcial PASS, requisito primário seletor FAIL**. Não é versão multilíngue funcional.

## Causa identificada por desassemblagem real do PE

A TEST4 instalava sua única BL no offset `0xD68BC` (VA `0x820D68BC`, opcode após alteração `482e6045`), que pertence a **OUTRA rotina de menu**, não ao `lvl_intro_update` que processa a tela original de Press Start. Testes isolados do wrapper nunca exercitaram o despacho completo do título, portanto não detectaram o erro.

A leitura da imagem mapeada original, combinada com o fonte fixado `n64decomp/sm64/src/menu/title_screen.c`, encontrou a rotina correta `lvl_intro_update(s16 arg,...)`:

| VA | Opcode original | Rota |
| --- | --- | --- |
| `0x82147414` | `7c6b0734` | `extsh r11,r3` — recebe argumento da intro |
| `0x82147434` | `4bffff8d` | caso 0: `intro_play_its_a_me_mario` |
| **`0x82147448`** | **`4bfffe31`** | **caso 1: `intro_regular` em `0x82147278` (Press Start real)** |
| `0x8214745C` | `4bfffecd` | caso 2: `intro_game_over` |
| `0x82147470` | `4bfffc01` | caso 3: `intro_level_select` |

A TEST4 interceptava outro caminho: o console nem chegava à rotina de seleção durante a abertura. **A causa do seletor ausente está comprovada pela localização errada da chamada**, mas o comportamento de renderização e a estabilidade da nova ligação ainda dependem do Xbox.

## Correção de código e regressão

- `scripts/multilang/title_only_selector.py`: `CALLSITE=0x82147448`, `ORIGINAL_INTRO=0x82147278`, `ORIGINAL_CALL_BE=4bfffe31`.
- `verify_native_title_dispatch`: confere a assinatura exata dos **quatro** despachos e proíbe que o hook da TEST4 em `0x820D68BC` permaneça na imagem. Falha antes de criar candidato se qualquer assinatura divergir.
- `scripts/multilang/test_title_only_selector.py`: nova regressão reproduz erro da TEST4 e garante que o ponto não pertencente ao título continue original.
- [GitHub Actions 38415812279](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38415812279): **PASS** para o seletor emulado e guardas de código, incluindo os novos testes; gerou binários PowerPC usados nesta TEST5.
- Dublagem continua **totalmente fora de escopo** por decisão explícita do proprietário.

## TEST5: compilação XEX Basic experimental REAL, ainda sem hardware

- **Arquivo:** `SM64_TEST5_SELETOR_TRILINGUE_TELA_INICIAL_30FPS.zip`
- **Arquivo de Biblioteca privada:** `/Xbox360 - SM64 PTBR/SM64_TEST5_SELETOR_TRILINGUE_TELA_INICIAL_30FPS.zip`; Library ID `libfile_7af70f58d3ec819189934e882f1fc729`.
- ZIP tamanho **17.184.588 bytes**, ZIP SHA-256 `4e28d292b8e50066e0e903c0ea310b053b2b5843fdb549068c197b8f70d3d8fc`; CRC PASS.
- XEX interno **17.182.720 bytes**, SHA-256 **`386a1516ee9a1da3475ac008dd3ddda4bf13fd92c779e38f6cafc038217ab7b6`**.
- PE mapeado recuperado do XEX após reconstrução, SHA-256 **`a6c0a1c451f6dd114f73bd324cb297d42f3ed6f6c027c8237d3244284e622672`**.
- **XEX Basic reconstruído com utilitário `xex2replace` já validado, a partir do arquivo TEST4 que abriu no console. Round-trip AES/PE byte a byte PASS**, não prova boot no Xbox.

### Diferenças binárias exatas TEST4 → TEST5

**14 bytes efetivamente distintos, em três intervalos somente:**

1. `0xD68BC` (4 bytes): restaurada a chamada de outro menu `4bfff68d`, removendo gancho incorreto TEST4;
2. `0x147448` (4 bytes): chamada correta do título `4bfffe31` → `482754b9` (BL ao wrapper `0x823BC900`);
3. `0x3BC900` (wrapper de 492 bytes): **somente duas BL internas foram recalculadas** para chamar a rotina `intro_regular` real em `0x82147278`; o restante do wrapper é byte-idêntico.

Verificação independente de diferenças: **todas as diferenças confinadas aos três intervalos, sem alteração dos dados .lang, tradução PT-BR, mapeamento B/Y, 30 FPS, save, áudio, resto do gameplay ou hook global `0x820CD128`**. Código de ativação para 170 diálogos e 26+90 nomes também byte-idêntico à TEST4.

## O que testar no Xbox 360

1. Em pasta **separada**, preservando TEST3 original estável e backups dos saves, abrir TEST5.
2. Confirmar se na tela de título (depois dos créditos) aparecem **Português / Español / English**; na falta da tela, informar imediatamente.
3. Se aparecer, usar D-pad UP/DOWN, A para confirmar, Start para entrar no menu normal de saves.
4. Depois validar idioma selecionado em diálogos, nomes de curso/estrela e, mais importante, entrar em fase, pegar estrela e retornar ao castelo. Repetir nos três idiomas gradualmente.
5. **Não declarar aprovação até receber feedback real**. Renderização com código antigo `print_generic_string_fade` fora do menu de saves não está garantida por simulação de CPU; possível novo problema de apresentação ainda não descartado.

## Estado do projeto

TEST5 **compilada e empacotada, não testada no hardware**. O objetivo final ainda é edição única PT/ES/EN, localizações equivalentes, controles Xbox 360 e seletor funcional, depois testes completos de gameplay/save/estrela/castelo. **Nenhuma etapa de dublagem permitida antes dessa validação e nova autorização explícita.**
