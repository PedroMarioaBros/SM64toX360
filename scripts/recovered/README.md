# Scripts recuperados do checkpoint de 17/09/2026

Esta árvore contém **cópias byte a byte** dos scripts recuperados do checkpoint
`SM64_PTBR_XBOX360_CHECKPOINT_COMPLETO_2026-09-17.zip`.

O ZIP original foi materializado novamente em 25/09/2026 com:

- tamanho: 80.704.194 bytes
- SHA-256: `265a6cdfba9e4dfaded578462a1388d4b97a1246643fd72d5ed8cdd4913e6368`
- manifesto interno: 56/56 arquivos aprovados

## Engenharia reversa

`engineering/`:

- `branch_refs.py`
- `extract_basic_xex.py`
- `scan_addr_refs.py`
- `scan_refs.py`

## Pipeline PT-BR 0.4

`ptbr_0_4/`:

- `analyze.py`
- `build.py`
- `check_rebase.py`
- `controls_probe.py`
- `pack.py`
- `reconstruir.py`
- `regression_menu.py`
- `stackstrings.py`
- `staticrefs.py`
- `verify.py`

## Dependências

Os scripts recuperados usam Python 3 e, conforme a etapa:

- `cryptography`
- `Pillow`
- `unicorn==2.1.4`
- ferramentas do host como `cpp`
- uma implementação XEX compatível nas etapas de repack da 0.4

## Entradas que NÃO ficam neste GitHub público

Os scripts foram preservados, mas seus dados proprietários/derivados não são
versionados automaticamente aqui. Exemplos:

- XEX original/corrigido/traduzido;
- imagens mapeadas;
- `text.raw` / `text.elf`;
- pacotes ZIP com o jogo;
- dumps e arte do jogo.

Os scripts esperam parte desses arquivos em caminhos relativos do projeto
histórico. Isso é intencional: o GitHub guarda a engenharia, não distribui o jogo.

## Fidelidade

Após a publicação, os 14 arquivos foram comparados pelo **Git blob SHA** contra os
arquivos extraídos do checkpoint. Todos os blobs publicados correspondem exatamente
aos originais recuperados.
