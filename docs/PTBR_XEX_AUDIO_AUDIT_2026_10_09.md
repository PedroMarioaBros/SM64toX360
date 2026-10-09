# Auditoria de áudio BPS × XEX — 09/10/2026

## Arquivos recuperados e verificados
- Patch: `SM64-PTBR-1.0-BMatSantos-Kosmus.zip`, SHA-256 `6e85270ff7d694e0e14ce3f99e5e29cc290c480066602542104a72cee0aa07d1`.
- BPS: SHA-256 `1a6a0d6acb3f9626d52ed8f6a71866007df059e494461984591887c509bef4a2`, CRC interno válido.
- Xbox 360: `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip` — arquivo interno `default.xex` SHA-256 `6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0`.
- Imagem PE mapeada do XEX: 17.170.432 bytes, SHA-256 `bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56`. Foi extraída usando cabeçalho XEX2 e descriptografia AES-CBC com a chave da seção de segurança, verificando assinatura MZ/PE.
- Arquivos binários não foram adicionados ao repositório público; código, relatórios e hashes foram adicionados à branch ativa.

## Resultado técnico novo
Foi criado `scripts/multilang/audit_bps_xex_overlap.py`, que:
1. valida CRC do patch BPS, lê ações SourceRead/TargetRead/SourceCopy/TargetCopy e marca bytes conhecidos sem inventar valores ausentes;
2. lê XEX2 Basic criptografado contido em ZIP ou XEX isolado e valida a imagem PE extraída;
3. mede cobertura de proveniência nas regiões áudio CTL/TBL;
4. procura fragmentos **byte-exatos** de 16, 32 e 64 bytes em janelas conhecidas do alvo BPS dentro da imagem PE do Xbox 360;
5. produz relatório JSON sem publicar ROM, XEX, conteúdo de áudio ou chaves.

| Região explorada no alvo BPS | Conhecidos | Dependentes da ROM |
| --- | ---: | ---: |
| CTL `0x57F8D0..0x597710` | 3.348 | 94.508 |
| Prefixo TBL `0x597710..0x60C040` | 96 | 477.392 |
| Dados TBL candidatos `0x60C040..0x794970` | 1.563.468 | 44.516 |

**Observação:** a última faixa é uma região exploratória, **não** o limite comprovado do banco TBL. Fragmentos conhecidos podem pertencer a dados novos da tradução; a inexistência de correspondência no port original não comprova ausência de áudio no XEX.

## Correspondência XEX × BPS
- 853 fragmentos de 16 bytes examinados, 0 correspondências exatas;
- 853 fragmentos de 32 bytes examinados, 0 correspondências exatas;
- 800 fragmentos de 64 bytes examinados, 0 correspondências exatas.
- Cada faixa conhecida foi amostrada de 2.048 em 2.048 bytes; **não** é prova exaustiva de ausência de correspondência para toda a ROM, e não é comparação semanticamente alinhada entre bancos de versões diferentes.

Resultado: **extração direta byte-a-byte não demonstrada**; o XEX poderá conter áudio em layout/codificação diferente. Não copiar bytes do PE indiscriminadamente para preencher lacunas da ROM.

## Verificação de código
- `scripts/multilang/test_audit_bps_xex_overlap.py`: 4 testes locais **PASS** (proveniência, corrupção CRC, detecção positiva e negativa de padrões).
- `docs/PTBR_XEX_AUDIO_AUDIT_2026_10_09.json`: saída real; Git blob conferido contra cópia local testada.
- Comando reproduzível: `python3 scripts/multilang/audit_bps_xex_overlap.py PATCH.zip XEX.zip --report relatorio.json`.
- Dependência adicional: `cryptography` para descriptografar o XEX.

## Próxima etapa
Investigar a organização das tabelas/samples do port no PE (referências e formato nativo Xbox 360), buscando correspondências **demonstráveis** entre samples originais e o material da fonte BPS. Para as vozes novas, conferir se os grandes blocos conhecidos podem ser delimitados por metadados CTL e livros ADPCM, sem decodificar amostras com coeficientes incompletos ou supostos. Alternativamente, buscar um pacote de amostras fornecido pelos autores.

**Sem dublagem PT-BR extraída/decodificada, sem novo XEX, sem validação de áudio no console.** A mecânica de crawling vertical continua pendente em trilha separada.

- Validação GitHub Actions confirmada em 09/10/2026: [Audit BPS-XEX provenance tests — run 37888054012](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37888054012), conclusão **success**; logs registram 4 testes PASS. Isso valida o parser e testes sintéticos, não uma extração de voz ou boot no Xbox.
