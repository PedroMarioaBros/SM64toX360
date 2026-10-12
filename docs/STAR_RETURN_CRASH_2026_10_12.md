# Falha de retorno ao castelo após estrela — 12/10/2026

## Relato confirmado em hardware pelo usuário

- Arquivo executado: `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip`.
- Resultado da abertura: texto e letras do menu reapareceram conforme desejado.
- **Falha:** ao obter uma estrela em uma fase e sair/retornar ao castelo, ocorre **Fatal Crash**.
- Pedro confirmou novo teste com o mesmo resultado. **Revogar a antiga classificação genérica de "aprovado/estável" deste pacote.** Menu passou, ciclo estrela→castelo **falhou**.
- O relato de travamento em compilação separada `TITLE_SELECTOR_TEST1` consta do histórico; não assumir que possui a mesma causa sem comparar os binários.

## Diagnóstico binário já executado

Os dois ZIPs originais foram recuperados da Biblioteca e seu `default.xex` descriptografado corretamente para PE.

| Item | TEST3 (controle) | Créditos/menu (falha após estrela) |
| --- | --- | --- |
| SHA-256 XEX | `b90ae1d1be953c1f817e9c64286c67da855778ac7c671098a3cd8495d8b6afd9` | `6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0` |
| SHA-256 PE mapeado | `a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c` | `bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56` |
| Chamada em `0xCD128` | `4bfc8321` = BL original `level_script_execute` | `482ef7d9` = BL ao gate próprio |
| Code cave `0x3BC900..0x3BCA08` | Zero em 264 bytes | Código experimental de créditos |

**Achado comprovado:** os dois PEs têm exatamente **226 bytes diferentes**, **todos** concentrados nos dois intervalos acima. Nenhum outro byte de código, tradução PT-BR, menus, saves, física, câmera ou áudio foi modificado entre os dois executáveis. Restaurar somente o hook original e o code cave vazio no PE experimental produz uma imagem **byte-idêntica** à TEST3 (SHA-256 exato).

**Interpretação:** um efeito colateral da rotina experimental de créditos é a principal hipótese, **não é causa comprovada** sem teste A/B na transição real estrela→castelo. Os testes anteriores simulavam `level_script_execute` e não modelavam o ciclo inteiro no console; CI estático PASS não prova estabilidade real.

## Novo pacote de teste A/B — executável real

`SM64_30FPS_TESTE_ISOLAMENTO_CRASH_ESTRELA_TEST3.zip`

- ZIP SHA-256: `02df1f67fba83e9d1cdd5f60ef3924f4fc48c58adb4555b372e69f2270d39893`
- ZIP com `default.xex`, instruções e metadados de auditoria; `default.xex` é a **mesma cópia original byte por byte de TEST3**, já preservada e assinada; **não foi recompilado nem repacotado internamente**, para evitar problemas de hash/assinatura do formato XEX.
- Biblioteca privada: `/Xbox360 - SM64 PTBR/SM64_30FPS_TESTE_ISOLAMENTO_CRASH_ESTRELA_TEST3.zip`, `libfile_0b550c3cf5b481919d988f4e302fc2c5`.
- Teste exclusivamente para isolar crash: extraia em **pasta separada**, preserve saves; abra mesma fase ou outra reproduzível, pegue estrela e confirme se voltou ao castelo.
- Se passar, a regressão estará associada à **introdução do gate** entre TEST3 e créditos. Se falhar também, devemos ampliar para TEST3/carga/save/outros aspectos do runtime.
- A TEST3 é controle de comparação, **não uma versão nova com créditos ou voz PT-BR**.
- Ainda **não há resultado de retorno ao castelo da TEST3 nesta rodada**. Não marcar bug como corrigido.

## Ferramentas e regressão

- `scripts/multilang/audit_star_return_regression.py`: lê os dois XEX Basic com SHA fixo, confere allowlist de diferenças e restaura PE de controle sem escrever XEX.
- `scripts/multilang/test_star_return_regression.py`: testes sintéticos para permitir somente os offsets previstos e reprovar mutações em outras regiões.
- Os dados de comparação estão igualmente presentes no `RELATORIO_COMPARACAO_BINARIA.json` do ZIP de teste.
- Nenhum XEX/ROM/áudio foi publicado no GitHub público.

## Dublagem — frente separada

- Os **seis WAVs PT-BR experimentais** permanecem preservados na Biblioteca; quatro com metadados completos e duas prévias de quadros sem loop validado.
- Ainda precisam de escuta/identificação das falas e não foram integrados a nenhum XEX.
- Prioridade de engenharia: primeiro garantir retorno de estrela sem crash; depois integrar progressivamente as vozes, verificando cada amostra/evento sem alterar texto PT-BR próprio, saves, 30 FPS ou controle A/B/Y.

## Próxima execução

1. Receber resultado A/B do teste no Xbox: PASS ou Fatal Crash, sem apagar saves.
2. Se TEST3 PASS, redesenhar créditos/seletor em fluxo `intro_regular/lvl_intro_update`, sem hook geral persistente em `level_script_execute` para o ciclo normal de fases; testar entrada/saída e retorno de estrela **antes** de reativar funções extras.
3. Se TEST3 também travar, auditar transição/save na base sem gate e reproduzir com um teste mínimo seguro.
4. Em paralelo, confirmar a qualidade e identidade dos seis WAVs por escuta e continuar auditoria de amostras sem metadados incompletos.

**Estado atual:** código/regressão estática analisados; binário A/B pronto; hipótese ainda não confirmada no console; nenhum novo fix ou dublagem em XEX.
