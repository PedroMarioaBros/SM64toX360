# TEST4 experimental — seletor trilíngue exclusivo da tela de título (12/10/2026)

## Resultado binário real

Foi construída a primeira **TEST4 XEX Basic experimental** sobre a TEST3 comprovadamente estável no Xbox (teste estrela→castelo), integrando a imagem tri-idioma EN/ES sem sobreposição com os controles B/Y. **Não foi testada em hardware** nesta execução, portanto não classificar como estável ou final.

- **XEX SHA-256:** `ae43067a1849d115a591c163df4f942e8f3f7a40e83a69029fac69dadd0920be` (17.182.720 bytes).
- **PE mapeado após reconstrução SHA-256:** `10549edf9a516b6b7099034519ea5973ed0ad989042d7a25a5b74155a1f729e1` (17.170.432 bytes).
- **PE de dados antes da ligação do seletor SHA-256:** `df139691efb4d146aca07215fa7becf3164a68ad4b778cadd575cd5ef04dfc76` (correção do COURSE3).
- **XEX round-trip AES-CBC + PE Basic:** **PASS** — descriptografar o XEX reconstruído novamente produziu um PE **exatamente igual ao PE candidato, byte a byte**, incluindo hash.
- **ZIP de teste privado:** `SM64_TEST4_SELETOR_TRILINGUE_30FPS_TESTE_XBOX.zip`; SHA-256 `3d1bd3ad11a49d88e0a742586e6b55cd202b4e4ad93fcb36719b7ea22b7405f8`; tamanho 17.185.690 bytes; ZIP CRC PASS.
- **Localização recuperável:** Biblioteca privada `/Xbox360 - SM64 PTBR/SM64_TEST4_SELETOR_TRILINGUE_30FPS_TESTE_XBOX.zip`, id `libfile_abecdb8e5ef081919667d1a3127f7ee7`. Não publicar XEX/PE em repositório público.

## Regressão detectada e corrigida antes da construção

O mapeador de atalhos B/Y da TEST3 usa `.lang+0x80` e `.lang+0x84` como campos dinâmicos por quadro (`scripts/multilang/direct_jumps.py`). A primeira versão de `install_trilingual_course_tables.py` havia armazenado o magic `COURSE3` e metadados em `.lang+0x80..0xB3`. Isto **colidia em tempo de execução** com os controles e os testes anteriores de tabelas sintéticas não o modelavam.

Correção efetiva:
- Deslocar **COURSE3 para `.lang+0xC0..0xF3`** (56 bytes de área exclusiva no header).
- Preservar **`.lang+0x80..0x87`** para B/Y (sem inicialização a dados constantes).
- Atualizar `course_table_activation.py` para ler metadados de tabela curso em `0x830400D8` e estrelas em `0x830400E4`.
- Atualizar as regressões estáticas e PowerPC. [Trilingual Course Staging CI 38337049995 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337049995); [Course Activation CI 38337053627 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337053627); [Dialog Delta CI 38337057570 PASS](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337057570).
- A imagem intermediária TEST3 foi reconstruída com o cabeçalho seguro, hash `df139691efb4d146aca07215fa7becf3164a68ad4b778cadd575cd5ef04dfc76`.

## Estratégia do seletor (sem hooks causadores do crash)

Foi comprovado no binário original que `lvl_intro_update`, durante `LVL_INTRO_REGULAR`, chama **exclusivamente** `intro_regular` a partir de `0x820D68BC` (instrução original `4bfff68d`).

O novo `scripts/multilang/title_only_selector.py` troca **essa única BL** por chamada a um wrapper na região previamente vazia `0x823BC900`:
- Enquanto o idioma não foi confirmado: chama o intro original temporariamente sem START e sem contador de demo automático; desenha os três nomes de idioma e um marcador, usando a rotina existente de texto; D-pad UP/DOWN navega; A confirma.
- A confirmação aciona as funções de seleção dos **170 diálogos** e das **26 áreas + 90 estrelas**; libera a execução original do título no próximo quadro, incluindo Start normal.
- Depois da escolha, chama o `intro_regular` original sem mudanças. O wrapper não é executado no ciclo de gameplay/retorno do castelo.
- A rotina geral `level_script_execute` em `0x820CD128` **permanece inalterada** (`4bfc8321`), assim como o início original de `intro_regular` em `0x820D5F48` (hook anterior associado à falha).

### Diferenças binárias auditadas na imagem candidata

| Região (offset de PE mapeado) | Finalidade | Bytes de código |
|---|---|---:|
| `0x3BC800` | Ativar os 170 diálogos | 88 |
| `0x3BC900` | Wrapper título seletor | 492 |
| `0x3BCC00` | Ativar 26 áreas e 90 estrelas | 148 |
| `0xD68BC` | Apenas BL de título | 4 |

**572 bytes efetivamente diferentes** entre o PE de dados seguro e o candidato com seletor, todos dentro dessas quatro regiões. Nenhum dado de tradução original PT-BR foi modificado nesta etapa, nem os dados `.lang` previamente revisados. SHA-256 do wrapper de 492 bytes: `66d84fb375d527d7d600595c3fe070461540820630d06aa205802b8a5a44a02f`.

### Validação

- [GitHub Actions Test Title-Only Xbox Language Selector run 38337444153](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337444153): **CPU PPC Unicorn PASS** com D-pad UP/DOWN, bloqueio temporário START, restauração de controlador, emulação de intro e preservação de B/Y.
- [GitHub Actions run 38337494648](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337494648): CPU PPC PASS incluindo **A de confirmação nos três idiomas**, que executou os algoritmos reais de cópia dos ponteiros sem alterar áreas adjacentes. Binários PowerPC gerados nesse run.
- [Build SM64 xex2replace run 38337505562](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38337505562): utilitário host para reconstrução do XEX **PASS**.
- Inspeção AES do XEX reconstruído localmente **PASS**, conteúdo interno coincide 100% com imagem candidata.
- **Não há GPU renderizada nem boot/teste real do Xbox**, e as rotinas de renderização existentes podem ter dependências não modeladas em emulação. O teste hardware deve começar por boot/tela do seletor.

## Roteiro de teste obrigatório no Xbox

1. Extrair em pasta separada e preservar TEST3 e saves. Fazer backup antes de iniciar.
2. Abrir `default.xex`. Na tela do título, verificar **IDIOMA / LANGUAGE, Português, Español, English** e marcador.
3. D-pad UP/DOWN muda seleção, A confirma, então Start entra no menu de saves.
4. Validar diálogo e título de fase/estrela no idioma selecionado.
5. Pegar estrela, voltar ao castelo e salvar/carregar. Repetir para cada idioma em sessões separadas.
6. Se falhar, relatar etapa exata, tela exibida, controle pressionado e se retornou ao castelo.

### Limites e regra de escopo

**Não concluído:** textos restantes de interface e menu de saves ES/EN, revisão editorial completa de equivalência entre os três idiomas e testes no hardware Xbox 360 com estabilidade de save/retorno. Este executável é exclusivamente **TESTE EXPERIMENTAL**, não release final.

**Dublagem absolutamente fora do projeto nesta etapa**, só retomar com nova autorização explícita após os três idiomas, tela de seleção, saves e gameplay funcionarem completamente e serem aprovados em hardware. Áudios originais continuam presentes.
