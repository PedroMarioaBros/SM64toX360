# TEST12 — relatório de patch estático da interface
Data: 20/10/2026

## Resultado da implementação no código

Foi criado `scripts/multilang/test12_live_ui.py`, um patcher fail-closed que exige a PE mapeada exata da TEST11 pelo hash `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`. O patcher altera somente o wrapper do seletor, a rotina auxiliar em cave livre, os metadados/tabelas de `.lang` e os novos dados anexados à cauda livre de `.lang`.

Execução local sobre a PE TEST11 recuperada:
- PE de entrada: 17.170.432 bytes; SHA-256 `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`.
- PE candidata gerada: SHA-256 `a71a6409b42de7e03db856654ba44540b462d3d71c5b650c6eb01c939ec6226b`.
- Wrapper: 584 bytes, dentro do cave de 768 bytes.
- Auxiliar de tradução do menu de saves: 108 bytes, dentro do cave livre de 256 bytes em `0x823BCB00`.
- 30 rótulos/strings de menu e estado/score preparados para PT-BR, Español e English, com verificação de que cada texto cabe no buffer existente.
- `.lang+0x80–0x87` (scratch B/Y) preservado byte a byte.
- Hook global de `level_script` preservado byte a byte.
- Estado inicial configurado para English (`index=2`).

## Testes automatizados

A workflow [TEST12 Trilingual UI Static and CPU Tests](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39377225771) passou em 20/10/2026: 4 testes estáticos e 5 cenários de CPU PPC. Ela verifica limites de código, buffers, prévia dinâmica com acentos, ordem/direcionais, prompt Start e cópia das strings do menu após A.

## Limitações e status real

- Smoke test específico no Xenia Canary Linux com renderizador nulo: TEST11 e TEST12 ficaram executando por 8 segundos sem mensagens de fatal/exception; o backend nulo registrou falhas de desenho esperadas e **não fornece validação visual**. Xbox físico ainda não testado.
- A prévia do seletor usa o renderizador nativo de glifos, com acentos codificados; a ordem visual é English → Español → Português e os IDs internos são 2=English, 1=Español, 0=Português. A aparência final dos glifos ainda precisa de validação visual.
- XEX candidata empacotada com `xex2replace`: SHA-256 `d4a15796f13e9239aeba02cc446b0a0224ae9579b3af8e5564469454e2427d06`. A extração/decriptação do payload e um segundo roundtrip reproduzem exatamente a PE candidata (`1a5ff2...`).
- Não foi alterado o sistema de dublagem; permanece fora do escopo.
