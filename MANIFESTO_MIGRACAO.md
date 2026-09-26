# Manifesto da migração

Auditoria iniciada em 25/09/2026 e ampliada na mesma retomada com recuperação
forense dos byte streams da linha Native60.

## Classes de evidência

- **RAW_RECUPERADO**: bytes reais recuperados e hash recomputado.
- **METADADO_SEM_RAW**: arquivo real localizado, mas sem byte stream materializado.
- **TEXTO_INDEXADO**: conteúdo textual recuperável, sem garantia de identidade do arquivo original.
- **HISTÓRICO_SEM_ARQUIVO**: menção comprovada no histórico sem artefato recuperado.

## Base e PT-BR — RAW_RECUPERADO

- `sm64corrigido.xex`:
  `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`
- PT-BR v0.4 XEX:
  `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`
- pacote base:
  `d146a3f57d7023648bbdbba7f2644296c793629dba4301fc12e157af7900297a`
- pacote PT-BR 0.3:
  `7123e27c52aa862e51e403a1bba52b94a7dc055eccc33f413bd31f253dad3dcf`
- pacote PT-BR 0.4:
  `d31bdd7d8396bbeeea2805dd9cdb3f7bfbfee106bf1fc2380b19bc76e33e2b78`
- checkpoint completo 17/09:
  `265a6cdfba9e4dfaded578462a1388d4b97a1246643fd72d5ed8cdd4913e6368`

O checkpoint foi materializado novamente com **80.704.194 bytes** e seu manifesto
interno passou em **56/56** verificações SHA-256.

## Linha 60 FPS — RAW_RECUPERADO

Todos os XEXs e ZIPs abaixo foram recuperados em bytes. Os hashes foram
recomputados nesta retomada.

| Versão | XEX SHA-256 | ZIP SHA-256 | mapped SHA-256 |
|---|---|---|---|
| v0.5 DIAG 60HZ DUPLICADO | `49cfaaa24a6164d8450aeb50551d31c9af5609d6d8c9f09da3bc702647ad542a` | `ddd4b759c075406f37c0b613b277205b3ca37b17c4b9446bdca5e8ce162cc893` | `a541c92e51d0af2cc5f32b4bc1b1f1268f5455acd5a6e53ecca93604f74b9a59` |
| v0.6 INTERPOLADO Y 30/60 | `07702be746b224c54bb43220c215fcb1b4c58f6b27c619a99a06d9f248b655df` | `0e11a86670242f7025c44b8f9b219a8623b7e065182f610e2973bb87db1f4a6c` | `e63fb087a2fabfbfbc451bc8557561b89dca93ecbdde011a9a349fdcd8fab21f` |
| v0.7 NATIVE60 CORE TEST | `51d898f1d027aff2ee28f16ea43ce89672c73c0bf2212c7b3bda015ba3389382` | `0809b12c5d184b18a60268a6026bc0e55ec6bee3764157fe797d021ccede76e9` | `4630aacb5011ec4726e8c852a05d09bf4acc1a9749913811d8267f00d6313312` |
| v0.8 RETIME CORE A | `ff5c185bc6a78c38b80b14c6923bc6d94f2ff733c6e1c8f0a3855dc6c11583f6` | `feb34fc42c0f63a309c16c68ac71b9383c3949abb328bd1368396436e8f18a3` | `b8eb88dfbb8fb11d418e17dec2693667586d4c0a3083708e43506bc838add6a2` |
| v0.9 FINAL60 RC1 | `7009c42c7962090d045d9e547037f1ff7c88f4992633903718afc41d00bfd856` | `a0b0b3658893243cf4682d57b65d1a6d6bea1c0467c7b346f8a8a56f2786eef8` | `9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12` |
| v0.10 NATIVE60 RC2 | `f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7` | `c3d67872da96a3f3646a6f62a10fadd0b9195220bf20e8817f913486ca5a3455` | `b87b33f3664aaefe3d7163d998f0535a666f13437b9f4d91f556bad49512426b` |

Os ZIPs originais também recuperaram relatórios/checkpoints técnicos que antes
estavam apenas mencionados no histórico.

## Reconstrução independente

Além de recuperar os originais, a cadeia abaixo foi refeita a partir das bases
anteriores:

- v0.7 a partir da v0.4: XEX idêntico ao original;
- v0.8 a partir da v0.7: XEX idêntico ao original;
- v0.9 a partir da v0.8: XEX idêntico ao original;
- v0.10 a partir da v0.9: XEX idêntico ao original.

Em todos os casos reconstruídos, o XEX foi reextraído e o mapped resultante foi
byte a byte idêntico ao mapped planejado/original.

## Política

Nenhum XEX, ROM, ZIP com conteúdo do jogo, dump ou imagem mapeada é publicado
automaticamente. O repositório público contém documentação própria, scripts de
reconstrução e registros técnicos.
