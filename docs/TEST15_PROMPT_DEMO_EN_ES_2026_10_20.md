# TEST15 — investigação do prompt da attract/demo

Data: 20/10/2026  
Base: TEST14, 30 FPS  
Estado: **candidata experimental; ainda não validada no Xbox 360 físico**

## Resumo da investigação

Recuperei a PE mapeada exata contida no XEX TEST14 usando o payload criptografado e validei a identidade pelo SHA-256 esperado: `6266c97deec43d4f43fe3c89bce2ebfb019ab220409702a35fccbd17b0878742`, 17.170.432 bytes. Isso desbloqueou a análise estática que estava pendente.

A varredura PPC encontrou no TEST14 dois branches relativos diretos para `print_intro_text` (VA `0x82098D18`): o callsite dentro do wrapper principal (`0x823BCF40`) e uma chamada ainda nativa em `0x820DBEF8`. A chamada em `0x820DBEF8` está no texto executável, dentro da função que começa em `0x820DBED8`; não é apenas um falso positivo de dados alinhados. A função também processa estado/entrada do controle. **A relação exata dessa chamada com o prompt observado na attract/demo continua sendo uma hipótese a confirmar no hardware.**

## Mudança da candidata TEST15

O patcher estritamente exige a PE mapeada exata da TEST14 e só altera os intervalos abaixo:

| RVA/VA | Antes | Depois | Objetivo |
|---|---|---|---|
| RVA `0xDBEF8`, VA `0x820DBEF8` | `4BFBCE21` | `482E1069` | Encaminha a chamada nativa restante para um wrapper específico do prompt em `0x823BCF60`. |
| RVA `0x3BCEF4`, VA `0x823BCEF4` | `4182004C` | `60000000` (NOP) | Evita que o caminho de prompt selecionado volte ao texto nativo apenas porque o ponteiro do controle está nulo. |
| RVA `0x3BCF60–0x3BCFDC` | 124 bytes zero | Wrapper PPC de 124 bytes | Com estado ainda não confirmado, delega à rotina nativa. Português também usa a rotina nativa. Español/English desenham as duas linhas de prompt com as tabelas de idioma já existentes, sem ler o controle. |

O wrapper foi disassemblado: os desvios de estado/Português chegam à chamada nativa em `0x82098D18`; as duas chamadas de desenho chegam a `PRINT_CENTER=0x8212B498`. O seletor principal, a navegação/confirmar, a centralização X=160 e o bloqueio da demo antes da confirmação não foram modificados pela candidata.

## Integridade e testes

- PE de entrada TEST14: 17.170.432 bytes; SHA-256 `6266c97deec43d4f43fe3c89bce2ebfb019ab220409702a35fccbd17b0878742`.
- PE TEST15: 17.170.432 bytes; SHA-256 `d1657528056df5f8c1257f3197a2674f69a46ff14dd090b682bea47f4be4a8b4`.
- Wrapper TEST15: 124 bytes; SHA-256 `2b3c39d949055c0a21584ad3d248cd5c55b3fb72dae459cd62d53bbc8e0eb913`.
- Bytes efetivamente alterados: 106, dentro dos três intervalos listados.
- XEX TEST15: SHA-256 `fcf76cbe7a5e8247341dd4215254eb8a759f989ab42700ccd305eaca09680cc1`.
- ZIP de teste: SHA-256 `89a2f45e778afcb031d642f2f5820246a67b2584dfbc95874f4883f69454f121`.
- Round-trip verificado: payload da XEX TEST15 descriptografado tem 17.170.432 bytes e coincide byte a byte com a PE TEST15 (hash igual).
- Testes locais de patch PPC/fixture sintético: **5/5 PASS**. O workflow CI para esses testes foi adicionado ao branch; o status remoto ainda deve ser consultado separadamente.

Os testes sintéticos/disassembly e a validação de round-trip não comprovam o comportamento no Xbox.

## Problema conhecido não resolvido

As letras G e U da tela do seletor continuam cinzentas. TEST15 não altera esse caminho e **não declara o defeito corrigido**. A hipótese de usar maiúsculas já falhou no teste físico TEST14 e não foi repetida.

## Teste físico solicitado

1. Usar uma pasta/cópia isolada, manter TEST14 disponível como rollback e não apagar/substituir saves.
2. Confirmar o seletor centralizado e ocioso, sem iniciar demo antes do A.
3. Selecionar English, confirmar A e aguardar o attract/demo: verificar se o prompt permanece `PRESS START`.
4. Reiniciar; selecionar Español, confirmar A e verificar se o prompt da attract/demo fica `PULSA START`.
5. Verificar se TEST14 não teve regressões observáveis: Português e slots vazios `NOVO/NUEVO/NEW`.
6. Se houver tela preta/crash, parar e voltar à TEST14. G/U cinzentas são conhecidas e ainda pendentes.

Base de 30 FPS preservada. Native60 e dublagem permanecem fora do escopo.
