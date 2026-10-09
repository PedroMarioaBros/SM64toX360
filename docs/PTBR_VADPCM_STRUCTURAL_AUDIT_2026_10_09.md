# Áudio PT-BR — auditoria estrutural VADPCM (09/10/2026)

## Objetivo e evidências
Investigação apenas de leitura de dois arquivos da Biblioteca:
- `SM64-PTBR-1.0-BMatSantos-Kosmus.zip`: SHA-256 `6e85270ff7d694e0e14ce3f99e5e29cc290c480066602542104a72cee0aa07d1`.
- `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip`, com `default.xex` SHA-256 `6d5d94f681796b66024c2b820908eee3c49f101f08ebdc87c4694c6da67824b0`.
- XEX descriptografado em PE mapeado de 17.170.432 bytes: SHA-256 `bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56`.

Referência de formato: `tools/disassemble_sound.py` do autor `bMatSantos/sm64-ptbr` define quadros VADPCM de 9 bytes (16 amostras PCM), `parse_book` com order=2, npredictors=2 e 64 bytes de coeficientes big-endian.

## Patch BPS: quadro comprimido identificável
Região **exploratória**, não fronteira real de banco: `0x60C040..0x794970`.
- 71 trechos de bytes conhecidos com >= 512 bytes.
- 62 trechos exibiram 100% de cabeçalhos plausíveis a cada 9 bytes em alguma das nove fases, considerando apenas **quadros completos dentro do trecho conhecido**.
- 63 de 71 trechos atingiram pelo menos 95% nesse critério.
- Total de **147.609 quadros completos e conhecidos** nesses 62 trechos com fase perfeita. Isso não significa 147.609 vozes ou quadros consecutivos do mesmo sample.
- No primeiro trecho `0x60C040..0x60D9E8` há **729 quadros de 9 bytes completos**, com cabeçalhos compatíveis em todos os 729. Há ainda bytes isolados/incompletos nas extremidades; não extrapolar o limite real do sample.
- Um filtro de 64 bytes alinhados aplicado ao CTL (`0x57F8D0..0x597710`) encontrou **43 possíveis regiões de coeficientes**: **27 com 62/64 bytes conhecidos** e **16 com 63/64 conhecidos**, **0 integralmente conhecidas**. Cada janela contém pelo menos 30 pares de 16 bits não nulos. São candidatos heurísticos, ainda não resolvidos por ponteiro real.

## Port Xbox 360: formatos compatíveis
Na imagem PE descriptografada:
- `0xA27D20`: aparece uma estrutura com cabeçalho completo big-endian `00000002 00000002` e 64 bytes de coeficientes não triviais, compatível com codebook VADPCM de `order=2`, `npredictors=2`.
- Detecção limitada à região PE a partir de `0x3C0000`, alinhamento de 8 bytes e >=30 pares não nulos: **452 candidatos a codebooks completos**. Isso é identificação por assinatura, não prova de que todos os 452 estejam referenciados pelo runtime.
- `0xA3FB10`: 64 quadros sucessivos de 9 bytes apresentam **64/64 cabeçalhos plausíveis**, com **562 dos 576 bytes não nulos** e **159 valores de byte distintos**. É forte evidência de stream comprimido real, diferente dos falsos positivos por preenchimento de zeros.
- Comparando somente os bytes conhecidos das 43 janelas parciais do BPS contra os 452 codebooks candidatos presentes no XEX: **0 correspondências mascaradas exatas**.

## Interpretação e limites
- **Avanço efetivo:** o patch contém fragmentos de áudio em formato de quadros VADPCM; o executável Xbox 360 contém estruturas de coeficientes e quadros compatíveis. É possível agora investigar a integração em nível de codec e estruturas.
- **Ainda bloqueado:** as janelas do CTL alterado não estão completas e não há mapeamento validado `evento de voz -> sample -> codebook -> loop/tuning`. Não reconstruir coeficientes por aproximação nem exportar WAV afirmando dublagem confirmada.
- A inexistência de correspondências exatas não desqualifica o uso do decodificador do port: o patch contém falas **diferentes** das originais.
- A análise não identifica quais quadros correspondem a Mario ou Peach; dezenas de longos trechos BPS podem incluir outras alterações sonoras.
- Nenhum binário do jogo foi publicado. Nenhum XEX novo foi produzido, nenhum teste no Xbox foi executado e a base 30 FPS permanece inalterada.

## Código e reprodução
- `scripts/multilang/scan_vadpcm_partial.py`: examina proveniência do BPS, fases de 9 bytes e candidatos a coeficientes. Entrada: ZIP/BPS, saída: JSON de metadados; nunca inventa bytes.
- `scripts/multilang/inspect_xex_sound_layout.py`: lê XEX Basic, confirma estruturas completas do PE e cruza dados conhecidos dos candidatos CTL com codebooks Xbox.
- Testes sintéticos: `scripts/multilang/test_vadpcm_partial.py` e `scripts/multilang/test_xex_sound_layout.py`.
- Comandos:
  - `python3 scripts/multilang/scan_vadpcm_partial.py PATCH.zip --report relatorio_frames.json`
  - `python3 scripts/multilang/inspect_xex_sound_layout.py PATCH.zip XEX.zip --report relatorio_xex.json`

## Próxima tarefa
Identificar endereços e registros de metadados no PE do Xbox (referências, estruturas de sample, loop, tuning, IDs de evento dos bancos 08/0A) e relacionar com o layout CTL/TBL do BPS. **Não** tratar codebook por assinatura como amostra associada sem ponteiro. Só extrair uma voz quando dados de áudio e coeficientes necessários estiverem completos e vinculados por evidência.
