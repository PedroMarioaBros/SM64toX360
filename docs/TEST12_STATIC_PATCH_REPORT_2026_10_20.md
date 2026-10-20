# TEST12 — relatório de patch estático da interface
Data: 20/10/2026

## Resultado da implementação no código

Foi criado `scripts/multilang/test12_live_ui.py`, um patcher fail-closed que exige a PE mapeada exata da TEST11 pelo hash `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`. O patcher altera somente o wrapper do seletor, a rotina auxiliar em cave livre, os metadados/tabelas de `.lang` e os novos dados anexados à cauda livre de `.lang`.

Execução local sobre a PE TEST11 recuperada:
- PE de entrada: 17.170.432 bytes; SHA-256 `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`.
- PE candidata gerada: SHA-256 `50fd4a1f07dcfccd232debfa48e656ac3618b2a3d6a676ca570c12888224ec30`.
- Wrapper: 564 bytes, dentro do cave de 768 bytes.
- Auxiliar de tradução do menu de saves: 108 bytes, dentro do cave livre de 256 bytes em `0x823BCB00`.
- 21 rótulos/strings de menu preparados para PT-BR, Español e English, com verificação de que cada texto cabe no buffer existente.
- `.lang+0x80–0x87` (scratch B/Y) preservado byte a byte.
- Hook global de `level_script` preservado byte a byte.
- Estado inicial configurado para English (`index=2`).

## Testes automatizados

A nova workflow [TEST12 Trilingual UI Static and CPU Tests](https://github.com/PedroMarioaBros/SM64toX360/actions/workflows/test-test12-live-ui.yml) passou em 20/10/2026. Ela verifica os limites do código, o tamanho de cada string e executa as instruções PPC reais do wrapper/auxiliar em emulação de CPU. Os cenários cobrem a prévia conforme o idioma destacado, o wrap do direcional, a localização do prompt Start e a cópia das strings do menu após A.

## Limitações e status real

- Os testes acima validam o patcher e a lógica PPC em CPU; não validam Xenia nem o Xbox 360 físico.
- A fonte colorida da tela de título não tem ainda suporte seguro comprovado para todos os glifos acentuados. Por isso a prévia do seletor usa transliterações sem acentos nesta candidata de código (por exemplo, `INGLES`, `ESPANOL`, `PORTUGUES`). Isso **não atende ainda à especificação ortográfica final** e precisa ser corrigido antes de considerar a interface pronta.
- A PE candidata foi gerada localmente para auditoria, mas ainda não foi empacotada em XEX nem testada em Xenia/hardware.
- Não foi alterado o sistema de dublagem; permanece fora do escopo.
