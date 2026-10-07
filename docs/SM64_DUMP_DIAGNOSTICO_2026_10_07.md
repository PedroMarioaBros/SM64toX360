# Diagnóstico do arquivo sm64_dump.txt — 07/10/2026

## Conclusão

O arquivo foi gerado pelo modo de diagnóstico gráfico presente na compilação de teste executada no Xbox 360. Não é save, não é asset de dublagem e não é necessário para o boot do jogo.

## Evidência

- Cabeçalho do próprio arquivo: `=== SM64 360 FRAME DUMP (path: game:\\sm64_dump.txt) ===`.
- Tamanho observado: 1.178.555 bytes.
- SHA-256 do arquivo recebido: `93350c14d91f5908aa00bfe753e01ca79a20e4f0ba65492d5b9ddc7a52c1b703`.
- O dump registra backbuffer 1280x720, estado de depth/renderização e 2.027 chamadas `gfx_sp_tri1`, encerrando com `=== END (2027 gfx_sp_tri1 calls dumped; uncapped) ===`.
- O mapeador de controles documentado em `docs/CONTROLES_XBOX360.md` registra `BACK + START` como solicitação do diagnóstico gráfico, com detecção de novo pressionamento.
- A rotina de teste `scripts/recovered/ptbr_0_4/controls_probe.py` verifica a mesma combinação escrevendo o pedido de dump no estado interno.

## Interpretação

A explicação mais provável é que BACK e START foram pressionados juntos (ou que a compilação de diagnóstico recebeu essa combinação durante a sessão). O dump pode ser criado ao solicitar o diagnóstico e só ficar visível na pasta do jogo após o fechamento/retorno ao dashboard, dependendo do flush do arquivo.

## Ação

Não apagar nem incluir esse arquivo no pacote do jogo. Ele pode ser removido manualmente pelo usuário se não for mais necessário; isso não altera save nem a instalação. Para testes de produto, usar uma compilação sem o diagnóstico gráfico ou evitar BACK+START. Nenhum XEX novo foi gerado nesta análise.
