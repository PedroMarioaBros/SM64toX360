# TEST5 sem seletor no Xbox → TEST6 visual diagnóstico — 17/10/2026

## Confirmação de hardware TEST5 (usuário)
A TEST5 `SM64_TEST5_SELETOR_TRILINGUE_TELA_INICIAL_30FPS.zip` **abriu e executou créditos, Aperte Start, menu de saves e jogo PT-BR, porém NÃO mostrou qualquer seleção de idioma**. A TEST4 já havia falhado da mesma forma. **TEST5 = SELETOR REPROVADO; não é versão multilíngue aprovada.** Não há teste relatado de retorno após estrela para TEST5.

## Auditoria real do binário TEST5
O XEX foi extraído e decriptografado localmente:
- SHA-256 do PE mapeado TEST5: `a6c0a1c451f6dd114f73bd324cb297d42f3ed6f6c027c8237d3244284e622672`.
- A TEST5 **contém** a BL `482754b9` em offset `0x147448`, que substituiu `4bfffe31` do TEST3 original.
- A TEST5 **contém** o wrapper PPC em `0x3BC900`.
- O estado estático da seção `.lang` em offsets `0x14` e `0x18` é `0`. Um estado não inicializado como "já selecionado" **no arquivo** não explica o comportamento; mutações de runtime ainda não foram vistas.
- Na lógica do wrapper, quando estado = 0, Start deveria ficar bloqueado e o retorno ao CALL_LOOP deveria ser zero. O fato de Start ter avançado indica que ele **não controlou o caminho executado**, mas não distingue sozinho desvio/callback não alcançado, estado modificado em runtime, renderização incompatível ou outra imagem lançada.
- O PE contém callbacks `lvl_intro_update` em dados de level script, mas verificar CALLSITE em arquivo e iniciar emulação **diretamente dentro do wrapper** não é teste de boot/tela no hardware.
- A certeza anterior de que a TEST5 corrigiria a origem da TEST4 era prematura. Não atribuir causa conclusiva sem evidência do fluxo real.

## TEST6 estritamente de DIAGNÓSTICO VISUAL, não seletor funcional
A TEST6 é derivada da TEST5 que abriu no Xbox. Nenhum novo código foi instalado. Trocar **apenas dois recursos ASCII de título de comprimento idêntico**:
- PE `0x778`: `APERTE` (6 caracteres) → `TESTE6` (6);
- PE `0x1C98`: `APERTE START` (12) → `TESTE6 START` (12).

**Apenas 12 bytes efetivamente diferentes no PE**, localizados nesses dois recursos; bytes de código do seletor original TEST5, controles B/Y, PT-BR dos 170 diálogos, saves e código do jogo fora desses recursos não mudaram. **Isto não corrige a seleção de idiomas**; apenas testa qual recurso de texto é desenhado no Xbox.

- ZIP `SM64_TEST6_DIAGNOSTICO_TITULO_TESTE6_30FPS.zip`, SHA-256 **`e3c580683b4d2167e9ca5d888b950c587e456ffcbf0cbc0501383867aa3e470f`**.
- XEX SHA-256 **`6089bee0bad628fb61e2ec7b97dc59a4e42c0eacba6d0d0a31bd145e9d5f087e`**, 17.182.720 bytes.
- PE mapeado novo SHA-256 **`98ec2515a57af928a91369b0cac24a4448aa619d95da63314162afb200a20e4f`**, 17.170.432 bytes.
- Reconstrução via xex2replace Linux host **PASS**; extração inversa AES XEX Basic → PE byte-idêntica **PASS**; ZIP CRC **PASS**.
- Pasta privada para recuperar: `/Xbox360 - SM64 PTBR/SM64_TEST6_DIAGNOSTICO_TITULO_TESTE6_30FPS.zip`; Library ID `libfile_c8eb020b0ce88191b0ca7c059e374cf1`. **Não subir binário/XEX ao GitHub público.**
- Código-fonte do diagnóstico: `scripts/multilang/test6_title_marker.py`, guardas em `test_test6_title_marker.py`, workflow `test-title-marker-probe.yml`. Somente marcador, sem trabalho com áudio.

## Único teste necessário ao proprietário agora
Instalar a TEST6 **em pasta nova**, preservando a TEST3 estável, e observar a tela onde geralmente aparece `APERTE START`. Comunicar apenas:
- **APARECEU “TESTE6”**: prova de que pelo menos esse novo recurso textual do binário TEST6 foi exibido; ainda precisamos descobrir por que o seletor não interceptou o fluxo;
- **CONTINUA “APERTE START”**: ou o jogo usa outro recurso de texto, ou há diferença no pacote executado/carregado; **não culpar automaticamente o usuário**.

Não é necessário entrar em fase, alterar saves nem tentar os três idiomas. Em caso de crash parar o teste. A análise do resultado decide qual rotina de apresentação da tela inicial investigar primeiro, antes de gerar outro falso candidato de seletor.

**Dublagem continua 100% fora do escopo** até todos os três idiomas, tela de escolha, menus e gameplay serem aprovados no Xbox e autorização posterior explícita.
