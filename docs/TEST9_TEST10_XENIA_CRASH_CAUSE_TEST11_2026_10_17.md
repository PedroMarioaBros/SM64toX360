# Diagnóstico em Xenia: causa do Fatal Crash TEST9/TEST10 e TEST11 corrigida — 17/10/2026

## Origem da investigação

- TEST3: versão canônica da jogabilidade/estrela→castelo já aprovada em Xbox real.
- TEST8: primeiro overlay visual dos idiomas comprovado por fotos reais do Xbox.
- TEST9: **FATAL CRASH real no Xbox** na passagem créditos→título/seletor, antes da escolha.
- TEST10: **três FATAL CRASHES reais** ao pressionar D-pad UP, D-pad DOWN e botão A; sem crash quando apenas mostrava os textos.
- Até esta investigação, o Xenia tinha sido iniciado com Vulkan por software e os XEX reais abriam, mas os botões do teste automatizado não eram confiáveis. Nunca promover TEST9/TEST10 como estáveis.

## Montagem de infraestrutura e correção de teste falso

Xenia Canary Linux **dac2794** (AppImage oficial, 16/10/2026) foi executado em Linux com Mesa **lavapipe/llvmpipe** e Xvfb. Sem GPU física. XEX reais privados foram carregados **localmente**, sem subir jogos ao GitHub público.

O teste automatizado original usava `--keybind_dpad_up=F5`, `...F6/F7/F8`; o **Xenia rejeitava** esses valores: `failed to parse binding "F5"`. A tecla de função F8 ainda acionou o painel de pós-processamento do emulador, contaminando uma tentativa de sequência. **Não confiar nos antigos PASS de envio host para F5–F8**.

Corrigido para teclas ordinárias/únicas (confirmadas no log do driver HID):
- `R` → D-pad UP;
- `T` → D-pad DOWN;
- `J` → Xbox A;
- `G` → Start.

Foi corrigido `scripts/xenia/replay_buttons.py` e seu CI para recusar bindings que o Xenia não confirmar. [Smoke CI de teclado, run 39028670106](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39028670106) **PASS**, mas **essa CI pública não contém jogo**. As observações abaixo usam os XEX privados em Xenia local.

## Reproduções reais do problema no emulador

| Executável | Condição em Xenia | Resultado |
|---|---|---|
| TEST8 original, título | pressionar A | sem CRASH DUMP |
| TEST9 original | chegar ao título, sem input | **CRASH DUMP** |
| TEST10 original | pressionar A | **CRASH DUMP** |
| TEST10 original | pressionar D-pad UP | **CRASH DUMP** |
| TEST10 com marcador `X→A` (1 byte) | D-pad UP / A | A colorida desenhada; **nenhum crash dump** |
| TEST9 com marcador `X→A` (1 byte) | chegada ao título | overlay visível; **nenhum crash dump** |
| TEST9 com marcador `X→O` (1 byte) | título / navegar / confirmar / menu de saves | **nenhum crash dump** |

**Assinatura de crash idêntica em Xenia TEST9/TEST10 originais:**
- `PC = 0x8215F1A4`;
- `Access Violation: read at 0x0000000100000000`;
- thread guest `0x00000006` — erro levantado durante processamento/renderização de textura.
- Todos os pontos acima foram registrados pelo **Xenia executando XEX reais**, não pela simulação Unicorn PPC32.

## Isolamento causal de um byte

O wrapper usa fonte colorida nativa `print_text_centered`, e nela o cursor `X` chama uma via de textura que chega a leitura nula no Xenia. A causa mais provável é **glifo `X` inválido/ausente no atlas colorido carregado**; a entrada exata do atlas ainda não foi identificada diretamente, então não alegar auditoria da tabela de texturas como concluída.

Correção controlada:
- TEST9 PE mapeado original SHA-256 `a405ba6e97c933298a1e24361423b7230f75957a4ee0c0ecfced21d957b2e641`;
- Endereço virtual da string do cursor `0x8305CA30`, offset do PE mapeado **`0x0105CA30`**;
- Substituir unicamente byte ASCII **`0x58` (`X`) por `0x4F` (`O`)**;
- PE mapeado TEST11 SHA-256 **`a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`**;
- **EXATAMENTE 1 byte efetivamente diferente** entre o PE TEST9 original e TEST11;
- Mesmo wrapper de 384 bytes, mesmo input, blocos PT/ES/EN, 170 diálogos, 26 nomes de curso, 90 estrelas, controles B/Y, saves, gameplay, hooks originais. Nenhum novo desvio.
- A cópia interna foi reconstruída como **XEX2 Basic com AES** por `xex2replace` e **decriptada novamente**, devolvendo o PE corrigido **byte-idêntico**.

A fonte auditável e fail-closed é `scripts/multilang/test11_safe_title_cursor.py`, testes `test_test11_safe_title_cursor.py`. [CI TEST11 Safe Title Glyph Regression **39028635499 PASS**](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39028635499). Não publicar PE/XEX no repo.

## Fluxos que passaram NO XENIA com cursor O

Xenia dac2794, XEX TEST11 real, entradas do emulador já verificadas nos logs:

- **Português**: A → `APERTE START` → Start → menu de saves, sem crash dump.
- **Español**: D-pad DOWN → **O** à esquerda de `ESPANOL` → A confirma → `APERTE START` → Start → menu de saves, sem crash dump.
- **English**: D-pad DOWN duas vezes → **O** à esquerda de `ENGLISH` → A confirma → Start → menu de saves, sem crash dump.
- **Bloqueio pré-confirmação**: tentativa de Start ainda na tela `IDIOMAS` não avança para saves.
- **Entrada no jogo**: após escolher Español e abrir saves, pressionar A sobre `MARIO A` iniciou a **cena inicial da princesa Peach**, sem crash dump nessa janela.

**Importantíssima pendência observada:** mesmo escolhendo Español, o menu de saves permaneceu em **português** (`ABRIR JOGO`, `PTS.`, `COP.`, `APAGA`, `ESTEREO`). Logo, a interface **não é inteiramente trilíngue**. Não chamar a TEST11 de versão final. Ainda não foram validados os diálogos das fases, salvar, pegar estrela e retornar ao castelo.

### Arquivos

- ZIP privado da candidata TEST11: `SM64_TEST11_SELETOR_TRILINGUE_GLIFO_SEGURO_CANDIDATA_30FPS.zip` — **17.185.804 bytes**, SHA-256 `175f8ab3dbb510827cde7d4156acd7f2f72c6beb482344a84ed2e813622d74d1`;
- `default.xex` corrigido: **17.182.720 bytes**, SHA-256 **`ff5a669976865a8ddf9e9f4a4158c19c05db7de682b316905cef8771343752f7`**;
- PE TEST11 SHA-256 `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`;
- ZIP CRC PASS; AES round-trip exato PASS;
- Biblioteca privada: `/Xbox360 - SM64 PTBR/SM64_TEST11_SELETOR_TRILINGUE_GLIFO_SEGURO_CANDIDATA_30FPS.zip`, id **`libfile_dc328d27eba08191b669d85ac3e8e1c7`**;
- O ZIP inclui `LEIA-ME_TEST11.txt` e `AUDITORIA_TEST11.json`, sem necessidade de ferramentas externas para o proprietário extrair a XEX.
- A TEST11 ainda **NÃO FOI TESTADA NO XBOX FÍSICO**; testes Xenia não garantem identidade de comportamento com hardware.

## Sequência posterior e pendências

1. Manter TEST3 como referência de gameplay hardware; TEST8 como visual hardware.
2. Manter a TEST11 como **candidata Xenia PASS, hardware pendente**, nunca release final.
3. Corrigir tradução faltante dos arquivos de save/menus para PT/ES/EN, e renderização dos acentos `Português` / `Español`.
4. Ajustar layout para não sobrepor a cabeça do Mario. Ajustar apresentação dos créditos personalizados quando a estabilidade estiver confirmada.
5. Ampliar regressão Xenia: entrar em fase, diálogos, obter estrela, retornar ao castelo e persistência de saves. Testar os três idiomas. Não prometer aprovação dessas fases antes de observação.
6. Somente então pedir validação pontual opcional no Xbox real. **No primeiro crash físico interromper; não insistir**.
7. **Dublagem 100% fora do escopo**, até aprovação de todo o jogo multilíngue e nova autorização explícita.


## Arquivo privado com imagens e logs de prova

Foi também criado e guardado em Biblioteca privada o ZIP **`SM64_TEST11_XENIA_PROVAS_PRIVADAS_2026_10_17.zip`**, **3.296.752 bytes**, SHA-256 **`599aa61f6d7dcb71293da0d5051ec03b40c4d4be759f771d1cf082a8e32a05b6`**, ID `libfile_aeba11abe7688191a7dc9549fdac72f9`. Contém capturas do Xenia mostrando o marcador alternativo no PT/ES/EN, a transição para `APERTE START`, o menu de saves ainda em PT-BR após ES e o início da cena Peach, além dos trechos de crash dump com PC e endereço da violação. **Não contém PE/XEX do jogo nem credenciais**. Não subir essas imagens/diagnósticos privados ao repositório público sem autorização.

### Auditoria adicional do fluxo emulada e regressões

- TEST9 **original** (sem pressionar nada): reproduziu **o mesmo crash dump** `PC: 0x8215F1A4`, `read at 0x0000000100000000` que a TEST10 original ao apertar A ou D-pad UP.
- TEST10 alterada **somente X→A** (1 byte) + D-pad UP: o marcador A foi visível ao lado de `PORTUGUES`, sem crash dump.
- TEST9 alterada **somente X→O** (1 byte) + D-pad DOWN: marcador O visível ao lado de `ESPANOL`; repetindo DOWN duas vezes, O aparece ao lado de `ENGLISH`.
- START antes de A não abre saves. A confirma. START depois de A abre `ABRIR JOGO`; A sobre `MARIO A` inicia cena Peach.
- O curso/esfera/estrela→castelo **não foi testado** no Xenia, de modo que ainda há verificação de gameplay pendente.
