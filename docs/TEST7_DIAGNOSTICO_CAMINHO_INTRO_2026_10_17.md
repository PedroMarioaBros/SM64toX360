# TEST7 — Diagnóstico decisivo da chamada de desenho na intro (17/10/2026)

## Por que não repetir a TEST4/TEST5

- TEST4 e TEST5 abriam normalmente, porém **nunca mostraram a escolha dos três idiomas**; não foram aprovadas nesse requisito.
- TEST6 **mostrou "TESTE6 START" em foto real do Xbox**, portanto pelo menos o novo recurso textual da abertura está efetivamente presente e foi renderizado no hardware.
- O código PowerPC da TEST5/TEST6 contém o hook em `lvl_intro_update → intro_regular` e o wrapper, mas o jogo continua permitindo Start antes de confirmar idioma. A causa dinâmica ainda não foi comprovada; emulações isoladas do wrapper não são prova de execução na intro real.
- Pelo fonte fixado `n64decomp/sm64`, tanto `intro_regular()` quanto `intro_game_over()` chamam `print_intro_text()` antes da checagem de Start; o mesmo texto também pode ser desenhado em demos. Precisamos separar **qual caminho realmente desenha a tela observada**.

## O que a TEST7 faz (NÃO é um seletor corrigido)

Base EXATA: XEX TEST6 reconstruído; PE TEST6 SHA-256 `98ec2515a57af928a91369b0cac24a4448aa619d95da63314162afb200a20e4f`.

Alterações confinadas a **6 bytes efetivamente diferentes** no PE mapeado, sem alteração de tamanho da imagem:
- `0x778`: mudar 1 byte final de `TESTE6` → `TESTE7`;
- `0x1C98`: mudar 1 byte final de `TESTE6 START` → `TESTE7 START`;
- `0x1472D4` (VA `0x821472D4`): substituir APENAS `bl print_intro_text` em `intro_regular()` (`4bf51a45`) por PPC NOP `60000000`.

**Intocados**: chamada `intro_game_over → print_intro_text` em `0x147368` (`4bf519b1`); código do seletor, sua BL em `0x147448`, todas as tabelas PT/ES/EN, os botões B/Y, áudio original, saves, ciclo fase→estrela→castelo e chamada global `level_script_execute` em `0xCD128`. O arquivo original da TEST3 permanece intacto e é o único jogo com retorno da estrela aprovado em hardware.

## Binários reais e verificação

- ZIP: `SM64_TEST7_DIAGNOSTICO_ABERTURA_NORMAL_30FPS.zip`, **17.184.703 bytes**, SHA-256 `de470eafeeae6be5ac6c1717405c69790e7892d3bbb98834ac79215d8204ba43`, CRC ZIP PASS.
- `default.xex`: 17.182.720 bytes, SHA-256 `089b887abc702359729249bdecb49d09f1412fd450aad6fc42739c7d3d5a9b81`.
- PE TEST7: 17.170.432 bytes, SHA-256 `cee2a0cbb4bbb7b47e867e387b13f81e71e72a2f60134851abedc9bfbd4986aa`.
- **Roundtrip exato:** XEX2 Basic AES reconstruído com utilitário validado → PE decifrado, corresponde ao PE modificado byte por byte PASS.
- **Regressão GitHub Actions [39007791041](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39007791041) PASS**, com guardas de 6 bytes, assinatura exata da TEST6, integridade de `.lang`, título, Game Over e hook global.
- Fonte: `scripts/multilang/test7_intro_path_probe.py`; testes: `scripts/multilang/test_test7_intro_path_probe.py`.
- **Backup privado:** Biblioteca `/Xbox360 - SM64 PTBR/SM64_TEST7_DIAGNOSTICO_ABERTURA_NORMAL_30FPS.zip`, id `libfile_ef25c163ece0819188b997a64fcdc6eb`; **NÃO publicar executáveis/PE no GitHub público**.

## Como interpretar a próxima observação em console

Testar em **pasta própria**, preservando TEST3 e saves. Basta executar o XEX até a cabeça do Mario na tela inicial, **sem carregar save nem jogar fase**.

| Observação na tela | Conclusão limitada mas útil |
|---|---|
| Mario aparece, **"TESTE7 START" não aparece** | Evidência de que o texto normalmente desenhado vem de `intro_regular`; a BL alterada dessa função é executada. Próximo: testar estado/ativação do wrapper sem pressupor que a renderização seja o único problema |
| Mario aparece **e "TESTE7 START" aparece** | A string está sendo desenhada por **outro caminho** (possivelmente `intro_game_over` ou demo), portanto não continuar tentando hooks exclusivos de `intro_regular` |
| Tela preta/travamento ou fluxo inesperado | **Interromper** e analisar a chamada original; não prosseguir em outras telas |

Isso é diagnóstico. **Não classificar TEST7 como seletor PT/ES/EN funcional.** A dublagem segue integralmente fora de escopo até a edição multilíngue estar estável no Xbox e nova instrução expressa.
