# Áudio no patch PT-BR — 08/10/2026

## Resultado reproduzido
Fonte de offsets: assets.json do repositório bMatSantos/sm64-ptbr, branch master, e ferramentas tools/disassemble_sound.py/extract_assets.py lidas nesta sessão.
Rastreamento dos comandos SourceRead/SourceCopy do BPS recebido por Pedro:
- Início CTL original 0x57B720 corresponde a 0x57F8D0 no alvo.
- Início TBL original 0x593560 corresponde a 0x597710 no alvo.
- Distância CTL→TBL: 97.856 bytes.
Isso corrige uma premissa de extração: não usar offsets da ROM original diretamente no alvo patchado.

## Cobertura sem ROM
No intervalo CTL 0x57F8D0..0x597710, o mapa de proveniência contém 3.348 bytes conhecidos e 94.508 desconhecidos.
Os primeiros 512 bytes do CTL estão todos dependentes da fonte. No TBL, 96 dos primeiros 512 bytes são conhecidos.
O intervalo exploratório 0x597710..0x794970 contém 1.563.564 bytes conhecidos e 521.908 desconhecidos; NÃO é uma delimitação confirmada do TBL completo.
Há longos trechos novos a partir de 0x60C040 e mudanças de coeficientes aparentes no CTL, mas sem tabela completa não é possível rotulá-los como amostras específicas e completas.

## Limites
Nenhuma amostra foi decodificada/ouvida; nenhum arquivo WAV/AIFF validado foi produzido; nenhum XEX foi alterado.
Não preencher bytes desconhecidos com zero e apresentá-los como áudio extraído.
A presença de lacunas na ROM total não prova impossibilidade de extrair vozes, mas agora há evidência de lacunas também nas tabelas necessárias.
O parser público exige ponteiros de amostra, tamanho, livro ADPCM, loop e afinação; esses campos precisam de verificação individual.

## Continuação
Comparar as estruturas de áudio do XEX base já usado no projeto com os campos da fonte requeridos pelo patch. Se houver correspondência comprovada, reutilizar apenas bytes verificáveis para completar tabelas/amostras e então decodificar.
Alternativa: pacote de amostras fornecido pelos autores. Pedro já informou não possuir a ROM; não repetir esse pedido como única próxima ação.
Script reproduzível: python3 scripts/multilang/map_bps_audio_anchors.py caminho/SM64-PTBR-1.0-BMatSantos-Kosmus.zip.
