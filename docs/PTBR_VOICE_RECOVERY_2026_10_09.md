# 09/10/2026 — recuperação parcial e primeiras prévias de voz PT-BR

## Descoberta principal

O XEX `SM64_DIAGNOSTICO_CREDITOS_MENU_CORRIGIDO.zip` contém, na seção `.data` do PE, os índices íntegros dos bancos de áudio do SM64:

| Estrutura | Offset **no arquivo PE** | Endereço virtual mapeado | Entrada |
| --- | --- | --- | --- |
| CTL | `0xA27B90` | `0x82A3AB90` | 38 bancos |
| TBL | `0xA3F9D0` | `0x82A529D0` | 38 bancos |

**Importante:** seção `.data` tem `PointerToRawData=0x3AD000` e `VirtualAddress=0x3C0000`. Endereços de arquivo e virtuais diferem em `0x13000` dentro desta seção; não tratá-los como iguais.

O parser inspecionou os bancos físicos **08** e **0A** do XEX:
- Banco 08: 27 instrumentos, 27 vozes originais, 27 bancos de coeficientes e amostras coerentes;
- Banco 0A: 24 slots físicos, 23 vozes originais; **slot físico 03 é nulo**;
- Total: **50 vozes originais com cadeias CTL→instrumento→descritor de amostra→codebook→loop→TBL estruturalmente verificadas**. Todos os cabeçalhos VADPCM de 9 bytes dentro das amostras originais examinadas passaram.

Os `voice_events.json` antigos listavam nomes sem o slot vazio: **não associar diretamente a posição da lista ao índice físico de instrumento do banco 0A.**

## Recuperação parcial do patch BPS

Usando somente os dois intervalos correspondentes aos índices e bancos de áudio originais presentes no XEX:

- Dados CTL originais XEX: 97.792 bytes copiados para o intervalo de fonte BPS que começa em `0x57B720` (o intervalo N64 publicado tem 97.856 bytes; os últimos 64 não foram inventados).
- Dados TBL originais XEX: 2.216.688 bytes copiados para a fonte BPS em `0x593560` (intervalo original publicado tem 2.216.704 bytes; os últimos 16 não foram inventados).
- BPS aplicado de forma **parcial, com máscara byte a byte de proveniência conhecida/desconhecida**. Nunca usar zero como substituto de byte desconhecido.
- Conhecidos antes de complementar com XEX: **1.718.881 / 9.090.352 bytes** do alvo.
- Conhecidos após complementar com os dois intervalos XEX: **3.361.841 / 9.090.352 bytes** do alvo; ganho de **1.642.960 bytes**.
- CTL traduzido `0x57F8D0..0x597710`: **96.951 conhecidos / 905 desconhecidos**.
- Região TBL de 2.216.704 bytes a partir de `0x597710`: **2.216.388 conhecidos / 316 desconhecidos**.
- No alvo, banco TBL 08 cresceu para **732.208 bytes** e banco TBL 0A para **831.920 bytes**; os áudios traduzidos são materialmente diferentes dos originais.

**Limitação fundamental:** não há a ROM N64 íntegra e não foi possível verificar o CRC32 `3CE60709` da *fonte completa* exigida pelo BPS. Logo, a equivalência dos intervalos XEX com a ROM fonte é uma hipótese tecnicamente forte baseada em estrutura e conteúdo, **não uma prova criptográfica**. Nunca declarar que reconstruímos a ROM completa ou dublagem integral.

## Quatro eventos decodificáveis sem lacunas

Quatro eventos têm **todos** os bytes do instrumento, descritor de amostra, dados VADPCM, codebook completo e cabeçalho de loop disponíveis na reconstrução parcial. Foram decodificados para arquivos WAV de 16 bits mono, 48 kHz, gerados apenas no ambiente privado de trabalho:

| Banco/slot físico | Evento candidato | Bytes ADPCM | PCM em amostras | Duração |
| --- | --- | ---: | ---: | ---: |
| 08 / 04 | Mario Yahoo | 20.862 | 37.088 | 0,773 s |
| 08 / 06 | Mario Hrmm | 13.420 | 23.856 | 0,497 s |
| 0A / 02 | Mario Panting | 15.328 | 27.248 | 0,568 s |
| 0A / 09 | Mario Punch Yah | 9.046 | 16.080 | 0,335 s |

- Nenhum byte faltante foi estimado para **essas quatro** amostras; todas as outras continuam bloqueadas por pelo menos uma lacuna ou metadado não verificável.
- O comprimento de loop de algumas gravações difere em até 1 amostra do comprimento de quadros VADPCM; a decodificação respeita o limite de quadros reais, sem criar conteúdo.
- O algoritmo Python segue a previsão da referência Nintendo 64 VADPCM, incluindo a matriz Q11 de 2 preditores e grupos de 8 amostras; sua saída PCM foi comparada com uma segunda implementação independente em **C** para os quatro eventos: **100% de igualdade byte a byte**.
- Esses arquivos são *prévias candidatas à dublagem PT-BR*. Identidade e qualidade de fala dependem de **escuta humana e validação de fonte**.
- ZIP privado de quatro WAVs com manifesto de hashes: SHA-256 `fca8f45be1faa5dec5aeea81200f5e5beb36c32e91b3e2931a2945dd1a30011d`, salvo na Biblioteca do projeto em `/Xbox360 - SM64 PTBR/SM64_PTBR_4_PREVIAS_EXPERIMENTAIS_2026-10-09.zip` (libfile `libfile_e46daa6cc8788191ba06e1cf87af923c`). O ZIP não está no repositório público.

## Código, evidências e testes

- `scripts/multilang/reconstruct_ptbr_audio_from_xex.py` — leitura XEX/BPS, reconstrução parcial com máscara, validação restrita de samples e opção local `--export-dir`. Travado nos hashes da dupla de arquivos auditada.
- `scripts/multilang/test_reconstruct_ptbr_audio_from_xex.py` — seis testes em dados sintéticos; falha de proveniência impede exportação; preserva slot 03 nulo.
- `docs/PTBR_VOICE_RECOVERY_2026_10_09.json` — metadados, medidas, SHA-256 individuais sem distribuir conteúdo dos áudios.
- CI [GitHub Actions run 37966469573](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37966469573): **6 testes PASS**, confirmado por logs. Teste sintético comprova o mecanismo de controle, não CRC da fonte N64 nem audição no Xbox.

## Próximos passos

1. Ouvir as quatro prévias e confirmar que os eventos correspondem à dublagem BMatSantos/Kosmus.
2. Investigar as 905 lacunas do CTL e 316 lacunas TBL por **offset de proveniência/source copy**; separar metadados faltantes daqueles sem relevância para samples específicos.
3. Procurar correspondências comprovadas em outras regiões do XEX ou metadados do autor para aumentar a quantidade de amostras válidas. Não reconstruir coeficientes ausentes por aproximação.
4. Não gerar novo XEX até confirmar uma estratégia de integração de vozes e preservar o port 30 FPS, menu/save e cannon fix.

**Estado real:** 4 prévias WAV experimentais geradas; 46 eventos originais restantes NÃO foram autorizados para exportação. Nenhum novo executável Xbox 360 nem validação no console.
