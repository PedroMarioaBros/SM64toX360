# Scripts

O checkpoint real de 17/09/2026 foi materializado e validado com **56/56 hashes
SHA-256**.

## Scripts do checkpoint

Os **14 scripts originais recuperados** da engenharia/PT-BR 0.4 estão em
`scripts/recovered/` e foram auditados contra os bytes do checkpoint.

## Reconstrução Native60

Quatro scripts determinísticos adicionais preservam a cadeia comprovada:

- `native60/reconstruct_v07_native60.py`
- `native60/reconstruct_v08_retime_core_a.py`
- `native60/reconstruct_v09_final60_rc1.py`
- `native60/reconstruct_v10_native60_rc2.py`

As reconstruções v0.7→v0.10 foram verificadas contra os XEXs originais
recuperados e produziram arquivos byte a byte idênticos.

## Política

Não são publicados XEXs, ROMs, ZIPs do jogo, dumps ou imagens mapeadas. Os
scripts contêm apenas engenharia própria/patches e validam suas bases por SHA.
