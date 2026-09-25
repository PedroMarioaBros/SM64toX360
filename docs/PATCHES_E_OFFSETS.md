# Patches e offsets recuperados

Os offsets abaixo são evidência técnica recuperada. Endereços da imagem mapeada não devem ser confundidos com offsets diretos no XEX criptografado.

## Correção 0.3 — menu de saves

- `NEW` em offset mapeado `0x3CD0B8`;
- `starIcon` em `0x3CD0BC`;
- `xIcon` em `0x3CD0C0`;
- instrução compartilhada `0x821432C4` preservada;
- usos dos ponteiros dos ícones em `0x821432CC` e `0x821432EC`;
- a 0.3 redireciona somente `0x82143348` para o texto do slot vazio;
- `PRESS` foi substituído por `APERTE` no espaço existente em `0x778`;
- `START` permanece em `0x780`.

A falha da 0.2 veio de tratar o endereço-base compartilhado como se fosse referência exclusiva a `NEW`, corrompendo os ícones de estrela/multiplicação.

## Menus/acentuação — diagnóstico após 0.4

Offsets documentados na imagem mapeada (base `0x82000000`): `PTS.` 0x3CD0D0; `COP.` 0x3CD0D8; `APAGA` 0x3CD0E0; `ESTEREO` 0x3CD080; `VER JOGO` 0x3CD0E8; `DUPLICAR` 0x3CD068 e 0x3CD10C; `COPIA CONCLUIDA` 0x3CD144; `HA DADOS SALVOS` 0x3CD158; `NAO` 0x3CD180.

Essas correções estavam **diagnosticadas, não aplicadas** na análise de 15/09/2026.

## Mapeador de controles

- wrapper: `0x8239E010`
- import `XamInputGetState`, ordinal `0x191`
- mapeador: `0x82165998` a `0x82165C90` (fim exclusivo)
- SHA-256 dos bytes do mapeador: `b51af5c7f53d6cf7a058a3353f9de40dfbe514890a0822427c151026904d3e03`

## Frame loop / 60 FPS

Checkpoint de 17/09: `exec_display_list` 0x8215CEF8; `produce_one_frame` 0x8215CF18; ponto de entrada preservado da 0.4 0x8239E3B8; base da imagem mapeada 0x82000000.

O progresso v0.9 registra code cave base 0x823BC7B8, tamanho 0x2F8 (760 bytes), final 0x823BCAB0, .text VirtualSize 0x32C7B8 → 0x32CAB0 e 29 entradas de patch.