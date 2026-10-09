# SM64 PT-BR — seis prévias de voz experimentais (09/10/2026)

## Resultado adicional da sessão

Depois das quatro WAVs exportadas com descritor, sample, codebook e cabeçalho de loop completos, duas outras amostras possuem **todos os quadros VADPCM de nove bytes e todos os 72 bytes do codebook conhecidos**, mas **o cabeçalho de loop possui lacunas**. É possível converter todos os quadros para um WAV **diagnóstico de reprodução única**, sem afirmar duração exata ou loop do jogo.

| Banco/slot | Evento candidato | Quadros | Tempo de todos os quadros | Estado |
| --- | --- | ---: | ---: | --- |
| 08/04 | Mario Yahoo | 2.318 | ~0,773s | WAV com loop header completo |
| 08/06 | Mario Hrmm | 1.491 | ~0,497s | WAV com loop header completo |
| 0A/02 | Mario Panting | 1.703 | ~0,568s | WAV com loop header completo |
| 0A/09 | Mario Punch Yah | 1.005 | ~0,335s | WAV com loop header completo |
| **08/16** | **Mario So Longa Bowser** | **3.794** | **1,265s** | **WAV com todos os quadros, sem loop header completo** |
| **0A/04** | **Mario Dying** | **5.438** | **1,813s** | **WAV com todos os quadros, sem loop header completo** |

As duas prévias novas usam 100% dos bytes dos samples comprimidos e dos codebooks que as descrevem. A saída PCM em Python foi comparada byte a byte com uma implementação independente em C — **idêntica nas duas**. As amostras comprimidas das duas prévias são **diferentes** das amostras originais do XEX nos mesmos slots, confirmado por SHA-256.

**Não confundir** duração de todos os quadros com duração exata usada pelo jogo: o loop header está parcialmente desconhecido. Nenhum byte foi inventado, interpolado ou removido no meio do sample. O final do stream pode incluir amostras de preenchimento, no máximo um quadro (16 amostras) além do último ponto de reprodução definido pelo jogo.

## Artefatos privados

- **Quatro WAVs de metadados completos**: Biblioteca `/Xbox360 - SM64 PTBR/SM64_PTBR_4_PREVIAS_EXPERIMENTAIS_2026-10-09.zip`; id `libfile_e46daa6cc8788191ba06e1cf87af923c`.
- **Duas WAVs de todos os quadros sem loop**: Biblioteca `/Xbox360 - SM64 PTBR/SM64_PTBR_2_PREVIAS_SEM_LOOP_2026-10-09.zip`; id `libfile_e50f6a2851808191a361137a33acc5cc`; ZIP SHA-256 `afae5732449c0490a85337c876eda90e4974636e8054e5c7c5afd465ebd333ff`.
- Manifesto/hashes públicos **sem áudio**: `docs/PTBR_SIX_VOICE_PREVIEWS_2026_10_09.json`.
- Rastreio das 1.157 lacunas que continuam fora dos bancos recuperados: `docs/PTBR_BPS_AUDIO_GAPS_2026_10_09.md`.

## Reprodução sem assets no GitHub

`scripts/multilang/decode_vadpcm_without_loop.py PATCH.zip XEX.zip --export-dir /pasta-privada --report relatorio.json`

- O script ignora eventos com loop header completo (já elegíveis para a exportação estrita).
- Exige ponteiro, instrumento, descritor, sample comprimido e codebook inteiramente conhecidos.
- Rejeita loop pointer fora de limites, bytes desconhecidos de sample ou codebook, dados VADPCM malformados e taxa inválida.
- Não interpreta o conteúdo de um byte ausente como zero.
- Na reconstrução do BPS, o XEX é uma **fonte condicional**: o CRC integral da ROM original N64 exigida pelo patch não foi validado.
- Arquivos de voz **não** foram publicados no GitHub público; somente scripts, testes e relatórios.

CI: [VADPCM no-loop frame diagnostics — run 37968449638](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/37968449638), **5 testes novos e 6 testes existentes importados (11 PASS)**; logs confirmados.

## Estado e continuidade

**6 WAVs experimentais** no total. Nenhuma ainda confirmada como dublagem PT-BR correta por escuta humana; **nenhum novo XEX**, nenhum boot no console. Base de 30 FPS, tradução PT-BR própria, câmeras, saves e correções já aprovadas preservadas.

Próximo passo técnico: classificar lacunas remanescentes por instrumento/descritor/codebook/sample e procurar provas de redundância autêntica no material disponível, sem tentar forçar outro áudio incompleto. Prosseguir com integração multilíngue somente após validar identidade de vozes e formato de reprodução.
