# Scripts

O checkpoint real de 17/09/2026 foi novamente materializado em 25/09/2026 e o
manifesto interno passou em **56/56 hashes SHA-256**. Assim, a existência dos
scripts abaixo está comprovada por bytes, não apenas pelo histórico.

## Pipeline PT-BR 0.4

Dentro de `projeto_0.4/projeto/ptbr-work/`:

- `analyze.py` — análise de diálogos/charmap e localização de estruturas.
- `build.py` — aplicação das alterações PT-BR sobre a imagem mapeada.
- `check_rebase.py` — preservação das alterações da base corrigida.
- `controls_probe.py` — teste isolado PowerPC do mapeador via Unicorn.
- `pack.py` — reconstrução/repack XEX da revisão 0.4.
- `regression_menu.py` — harness PowerPC de regressão dos menus.
- `stackstrings.py` — localização de textos montados na pilha.
- `staticrefs.py` — levantamento de referências estáticas.
- `verify.py` — verificação estática, hashes XEX e round-trip.

Também existe `projeto_0.4/projeto/reconstruir.py`, que recompõe a tradução a
partir da base corrigida esperada e de uma ferramenta XEX compatível.

## Engenharia reversa

Dentro de `engenharia_reversa/`:

- `extract_basic_xex.py`
- `scan_refs.py`
- `scan_addr_refs.py`
- `branch_refs.py`

## Política de publicação

Os scripts são código próprio/auxiliar e podem ser revisados individualmente para
migração ao GitHub. Entradas necessárias a eles que sejam binários, dumps, imagens
mapeadas ou conteúdo derivado do jogo permanecem fora do repositório público.

Esta pasta não deve receber placeholders nem versões reescritas “de memória”.
