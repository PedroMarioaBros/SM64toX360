# TEST11 — mapa estático da interface para correção trilingue
Data: 20/10/2026

## Base efetivamente examinada

O ZIP TEST11 foi recuperado da biblioteca do projeto e seu `default.xex` foi decifrado para a imagem PE mapeada, sem alterar o arquivo original. Os hashes coincidem com a auditoria TEST11 já registrada:

- XEX: 17.182.720 bytes; SHA-256 `ff5a669976865a8ddf9e9f4a4158c19c05db7de682b316905cef8771343752f7`.
- PE mapeada: 17.170.432 bytes; SHA-256 `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`.
- Wrapper atual do seletor: VA `0x823BCD00`, 384 bytes; SHA-256 `7198267b6f0e7699f5226637cd5db7e5f9470d5b5f3b9aac69e8d6e2ac0db6b1`.
- Região `0x823BCB00–0x823BCBFF`: 256 bytes zerados na PE TEST11, candidata a rotina auxiliar após validação de todas as referências.
- Cursor atual da seção `.lang`: `0x1CA32`; capacidade `0x20000`.
- **Restrição absoluta:** `.lang+0x80–0x87` (`0x83040080–0x83040087`) permanece reservado ao scratch do mapeamento B/Y e não pode ser usado por tabelas novas.

## Indicação “APERTE START”

A rotina de texto original está em `0x82098D18`. Ela desenha duas strings separadas, em `0x82000778` (`APERTE`) e `0x82000780` (`START`), nas posições usadas pela tela de título. As strings ficam na seção de dados somente leitura; a solução preferida é escolher os ponteiros/textos de renderização conforme o idioma, sem escrever nelas em tempo de execução.

Texto pretendido após confirmar:
- PT-BR: `APERTE` + `START`.
- Español: `PULSA` + `START`.
- English: `PRESS` + `START`.

Se o controle não estiver disponível, preservar o comportamento nativo de aviso de controle.

## Strings observadas no menu de saves

Os endereços abaixo são **offsets na PE mapeada**, não endereços MIPS/N64. O texto usa o mapeamento de glifos do jogo, não ASCII:

| Offset PE | Texto atual |
|---|---|
| `0x3CD050` | VOLTAR |
| `0x3CD05C` | VER PONTOS |
| `0x3CD068` | DUPLICAR |
| `0x3CD074` | APAGAR |
| `0x3CD080` | ESTEREO |
| `0x3CD088` | MONO |
| `0x3CD090` | FONES |
| `0x3CD0C4` | ABRIR JOGO |
| `0x3CD0D0` | PTS. |
| `0x3CD0D8` | COP. |
| `0x3CD0E0` | APAGA |
| `0x3CD0E8` | VER JOGO |
| `0x3CD0F4` | SEM DADOS SALVOS |
| `0x3CD10C` | DUPLICAR |
| `0x3CD118` | COPIAR PARA ONDE? |
| `0x3CD12C` | SEM DADOS SALVOS |
| `0x3CD144` | COPIA CONCLUIDA |
| `0x3CD158` | HA DADOS SALVOS |
| `0x3CD16C` | SEM VAGA |
| `0x3CD175` | FILE |
| `0x3CD17C` | NAO |

As capacidades de cada string variam porque algumas strings ficam imediatamente ao lado de outras. Qualquer cópia em tempo de execução precisa respeitar os limites exatos e o terminador `0xFF`; não sobrescrever rótulos adjacentes. As traduções devem caber nos buffers existentes ou exigir uma alteração comprovada das referências, nunca uma escrita especulativa.

## Estado da implementação

- O teste físico já confirmou que os textos internos do jogo acompanham PT-BR, Español e English após confirmar A.
- A tabela de prévia dinâmica foi prototipada na variante `pregame_gate.py`, com testes de CPU aprovados, mas **essa variante não é o wrapper TEST11 físico** (`0x823BCD00`). Não tratá-la como uma nova build para o console.
- A correção da build TEST11 deve partir da PE acima, modificar o wrapper real, manter B/Y e saves intactos e adicionar testes de CPU para prévia, prompt Start e cópia segura das strings do menu.
- Nenhuma nova PE/XEX de jogo foi publicada por este relatório. Não há alegação de validação Xenia/hardware para uma versão nova.
