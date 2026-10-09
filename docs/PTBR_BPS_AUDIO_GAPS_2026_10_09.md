# SM64 PT-BR — rastreamento de lacunas BPS (09/10/2026)

## Correção comprovada da leitura do XEX

O arquivo PE do XEX aprovado possui CTL começando em offset de arquivo `0xA27B90` e TBL em `0xA3F9D0`. A distância entre os dois é exatamente `0x17E40`, igual à distância dos anchors na ROM N64 fonte (`0x593560 - 0x57B720`).

Na versão anterior do script, eram recuperados apenas `0x17E00` bytes do CTL, ignorando **64 bytes finais de padding**, comprovadamente zero dentro do XEX. O TBL original tem mais 16 bytes zero após o término do último banco, agora também incluídos no bloco que equivale ao intervalo da ROM original.

O script de recuperação `scripts/multilang/reconstruct_ptbr_audio_from_xex.py` foi corrigido para ler `CTL_BYTES=0x17E40` e `TBL_BYTES=0x21D300`; aborta se o padding não tiver os zeros esperados ou se as fronteiras CTL/TBL não estiverem alinhadas.

**A equivalência do XEX à ROM integral CRC32 3CE60709 permanece condicional.** Padding zero comprovado no XEX não constitui prova de CRC da ROM original.

## Proveniência das lacunas

Auditoria real do alvo BPS após a correção:

| Área | Bytes conhecidos | Bytes desconhecidos | Trechos desconhecidos |
| --- | ---: | ---: | ---: |
| CTL `0x57F8D0..0x597710` | 97.015 | 841 | 63 |
| TBL `0x597710..0x7B4A10` | 2.216.388 | 316 | 34 |
| Total de bytes do **alvo BPS de 9.090.352 bytes** conhecidos (incluindo regiões fora do áudio) | **3.361.921** | — | — |

**Todos os 1.157 bytes ainda desconhecidos nessas duas áreas** apontam, pela decomposição das ações BPS, para deslocamentos da **ROM fonte fora dos intervalos de áudio recuperados**. É possível que o BPS tenha explorado correspondências de bytes de áreas de ROM não relacionadas ao som. Portanto, ampliar novamente CTL/TBL no XEX não resolverá esses 1.157 bytes.

**Distribuição nos bancos de vozes:**
- Banco 08: CTL 405 desconhecidos em 30 trechos, TBL 207 desconhecidos em 22 trechos.
- Banco 0A: CTL 436 desconhecidos em 33 trechos, TBL 109 desconhecidos em 12 trechos.
- Lacunas nos demais bancos/áreas exploradas são tratadas separadamente; não usar totais de banco como quantidade de vozes recuperáveis.

A trilha de origens rastreia `SourceRead`, `TargetRead`, `SourceCopy` e `TargetCopy`, inclusive cópia sobreposta. Código: `scripts/multilang/trace_audio_dependency_gaps.py`, testes `scripts/multilang/test_trace_audio_dependency_gaps.py`. O relatório de resumo é `docs/PTBR_BPS_AUDIO_GAPS_2026_10_09.json`. Relatório local com os endereços fonte de cada lacuna: SHA-256 `2e105bd72f31ad26eef36ed2221c03b7fb6d45545c60f73caaeb7f4db58f1fa2`, fornecido fora do GitHub.

CI: [Audit BPS audio dependency gaps — run 37967913594](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37967913594), **4 testes de rastreamento PASS**.

## Comparação das quatro primeiras prévias com áudio original Xbox

Os samples comprimidos do patch têm hashes SHA-256 diferentes das amostras originais do XEX nos mesmos slots físicos: banco 08 slots 04 e 06, banco 0A slots 02 e 09. Comparação e hashes individuais estão no JSON. Isso comprova dados diferentes, **não** que as falas são espanhol/português, nem que já foram ouvidas/validadas.

## Implicação

Não inventar bytes nem decodificar samples/codebooks incompletos. Para prévias de execução única, um cabeçalho de loop incompleto **não impede a conversão de todos os quadros** se o descritor, os dados comprimidos e o codebook estão completos; essa possibilidade é tratada em `docs/PTBR_SIX_VOICE_PREVIEWS_2026_10_09.md`.

**Sem novo XEX, sem qualquer alteração no binário estável de 30 FPS.**
