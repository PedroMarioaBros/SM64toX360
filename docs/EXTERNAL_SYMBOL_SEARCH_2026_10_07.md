# Busca externa por símbolos e referências — 07/10/2026

## Fontes consultadas
- `sirdankz/MKart360`: port público de Mario Kart 64 para Xbox 360, com solução Visual Studio/Xbox 360 e script de build. É evidência de um fluxo público de compilação XEX, mas não contém o código do Super Mario 64 nem símbolos aplicáveis ao nosso PE.
- `TheGag96/sm64-port`, branch `extended_moveset`: contém as rotinas de referência `push_or_sidle_wall`, `act_standing_against_wall`, `act_crawling` e o código comum de colisão. Não contém a mecânica de crawling aderido à parede nem um mapa PowerPC/XEX do nosso port.
- `sm64-port/sm64-port` e documentação/doxygen pública: fornecem nomes e relações de funções da decompilação, mas os endereços são da plataforma/build de origem e não podem ser transferidos diretamente para o PE Xbox 360.
- `ClementDreptin/XexUtils`: ferramentas gerais de aplicações Xbox 360, sem símbolos específicos do nosso jogo.

## Conclusão
Não foi localizado um mapa de símbolos, ELF/PDB, build reproduzível ou XEX público que corresponda ao `SM64toX360`/base v0.4 usada neste projeto. As fontes externas servem para confirmar a arquitetura lógica, não para escolher endereços.

## Próxima ação
Continuar a busca por artefatos específicos do port (logs de build, mapas, símbolos, commits antigos e branches) e, em paralelo, melhorar o cross-reference local por fluxo de registradores. Nenhum endereço externo será aplicado por semelhança.
