# TEST8 visual aprovado em hardware → TEST9 com seleção interativa — 17/10/2026

## Resultado real da TEST8 no Xbox 360

O proprietário enviou **duas fotografias da tela do console**. Ambas mostram as quatro linhas desenhadas usando a fonte colorida nativa da introdução:

- `IDIOMAS TESTE8`;
- `PORTUGUES`;
- `ESPANOL`;
- `ENGLISH`.

Uma das fotografias mostra ainda **`TESTE8 START`**, que não foi bloqueado nem removido na TEST8 visual.

**Conclusão: TEST8 = PASS VISUAL REAL**, via desvio exclusivamente na chamada comprovada `intro_regular → print_intro_text` em `0x821472D4`, wrapper `0x823BCD00` e renderizador nativo `print_text_centered` em `0x8212B498`. Esse teste não comprova que havia navegação, troca efetiva de idioma nem retorno de estrelas.

As imagens também confirmam um defeito de layout: título e opções ficam sobrepostos ao rosto/boné do Mario. Isso exige reduzir e reposicionar os rótulos, independentemente do input. São observações feitas sobre **fotos de hardware**, não uma renderização de emulador.

## TEST9: nova implementação interativa, ainda pendente de Xbox

A TEST9 conserva o ponto **efetivamente comprovado** de renderização da TEST8. Em vez de reutilizar o hook global `level_script_execute` que provocou crash, substitui somente o pequeno wrapper gráfico em `0x823BCD00` dentro de intro_regular.

**Fluxo planejado:**
1. Nos créditos e na abertura anterior, o motor normal permanece intacto.
2. Durante intro_regular, o wrapper lê `.lang+0x14` (estado) e `.lang+0x18` (índice, 0 PT-BR, 1 ES, 2 EN).
3. Se ainda não selecionado: mascara **somente START (0x1000)** de `gPlayer1Controller->buttonPressed` em `0x823C8990 + 0x12`, antes da verificação nativa em intro_regular. Não altera outros botões; START se renova normalmente a cada amostra do controle.
4. D-pad UP (0x0800) e DOWN (0x0400) alteram índice ciclicamente; desenha um **X** na linha escolhida com a mesma fonte nativa.
5. Botão A (0x8000) executa as rotinas PowerPC já preparadas em `0x823BC800` e `0x823BCC00`: copia **170 ponteiros de diálogos, 26 de nomes de áreas e 90 de estrelas** da língua selecionada. Atualiza estado=1.
6. Com estado=1, chama `print_intro_text` original e permite que o START execute normalmente o menu de saves.

**Região do controle verificada:** o código original `intro_regular` contém `lis r11,0x823D; lwz r11,0x8990(r11)`, que, por causa do deslocamento PPC *com sinal*, endereça **`0x823C8990`**, não `0x823D8990`. O código da TEST9 reproduz exatamente essa operação. É informação importante para as próximas versões.

**Melhorias visuais provisórias:**
- Cabeçalho `IDIOMAS`, sem `TESTE8`;
- Nome `PORTUGUES`, `ESPANOL`, `ENGLISH` à esquerda e mais distantes do rosto;
- `X` móvel ao lado do idioma ativo;
- `A CONFIRMAR` no canto inferior esquerdo;
- texto `APERTE START` só depois de confirmar A.

**Acentos e letras minúsculas ainda não disponíveis nesse renderizador:** `print_text_centered` usa um índice de glifos alfanuméricos ASCII e não reconhece `ê`/ `ñ` como no texto dos diálogos. Os nomes finais exigidos `Português` / `Español` / `English` precisarão de adaptação do atlas/tipo de fonte depois que a navegação for aprovada. Os diálogos EN/ES e seus glifos já instalados permanecem intocados nesta TEST9.

### Binários TEST9 e integridade

- **ZIP candidato:** `SM64_TEST9_SELETOR_FUNCIONAL_CANDIDATO_30FPS.zip`, tamanho **17.189.374 bytes**, SHA-256 **`01ef0d3de8eead10960665268daccf5d7b944bd10e741c7facdaf6d7ee98abbc`**, ZIP CRC PASS.
- **XEX interno:** `default.xex` 17.182.720 bytes; SHA-256 **`1b29d111f234df0515c0a21e964bf9866061c4688d4f0b2a74e741a61c320f07`**.
- **Imagem PE mapeada:** 17.170.432 bytes; SHA-256 **`a405ba6e97c933298a1e24361423b7230f75957a4ee0c0ecfced21d957b2e641`**.
- **Fonte da build:** PE TEST8 que passou em hardware, SHA-256 `fab6a7c31d1fa2cb4aea3ad5e0f3171bde5248a13f48bbcab56d2bc05fc4c438`.
- **Diferenças efetivas TEST8→TEST9:** **343 bytes** confinados a: wrapper `0x3BCD00..0x3BCFFF` (384 bytes usados), duas strings de marcador TESTE8→APERTE, cursor .lang e novas strings ASCII anexadas. O callsite comprovado `0x1472D4` permanece o mesmo. `lvl_intro_update` tem sua chamada original restaurada e `level_script_execute` permanece original.
- **XEX2 Basic round-trip PASS:** extrair e decriptografar o XEX reconstruído gerou PE **byte-idêntico** ao candidato. O resultado é validade de empacotamento, não garantia de boot.
- **Código PowerPC de seleção:** 384 bytes, SHA `7198267b6f0e7699f5226637cd5db7e5f9470d5b5f3b9aac69e8d6e2ac0db6b1`. Cave `0x823BCD00` com 0x300 bytes reservados; sem sobrescrever código vizinho.
- **Espaço .lang remanescente:** 13.774 bytes, preservando 170 diálogos PT-BR originais, tabelas PT-BR, B/Y e material trilíngue existente.
- **Pacote fonte/auditoria:** ZIP contém `scripts/test9_selector_native.py`, `TEST9_FINAL_AUDIT.json` e `LEIA_ME_TEST9.txt`.
- **Backup privado recuperável:** Library `/Xbox360 - SM64 PTBR/SM64_TEST9_SELETOR_FUNCIONAL_CANDIDATO_30FPS.zip`, ID `libfile_91fb0786f8188191ab908711b38534a9`. Arquivos binários do jogo **não publicados no GitHub público**.

### Testes técnicos efetivamente executados

1. [GitHub Actions TEST9 PPC Runtime — 39010181667](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39010181667): **5 testes PASS** em Unicorn PPC, executando os mesmos 384 bytes do wrapper usado no XEX, simulando título, controlador nativo, A/Start, D-pad e as cópias para PT/ES/EN.
2. [GitHub Actions TEST9 PPC + Source Reproducibility — 39010452532](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39010452532): **8 testes PASS** (5 CPU + 3 de reprodução de código e proteções), incluindo produção do mesmo SHA de 384 bytes pela fonte Python pública.
3. Auditoria local real de bytes da TEST8 para TEST9: **343 diferenças todas dentro da allowlist**, nenhum ponteiro dos diálogos preexistentes alterado, nenhum byte de B/Y ou hook global alterado.
4. XEX→PE criptografia round-trip exato PASS e ZIP CRC PASS.
5. **Não houve teste de boot, renderização, navegação, botão A ou estrela→castelo da TEST9 no Xbox real.** Não marcar aprovada nem estável.

### Como testar no Xbox (poucos passos)

Preservar TEST3 e fazer backups dos saves. Extrair TEST9 em **pasta isolada**:

1. Conferir se aparece `IDIOMAS` + três opções com indicador X, na faixa esquerda da tela.
2. Pressionar **Start ANTES de A**: não deve avançar ao menu de saves.
3. Testar UP/DOWN no D-pad: marcador X deve percorrer opções e voltar ciclicamente.
4. Selecionar um idioma e pressionar **A**: opções devem desaparecer, surge `APERTE START`.
5. Pressionar **Start**: abre o menu habitual de saves. Se qualquer etapa falhar, comunicar exatamente qual.
6. Se as etapas anteriores passarem, verificar um diálogo e nome de estrela na língua escolhida. Só após confirmar a interação básica testar ciclo estrela→castelo, saves e restantes idiomas.

Se ocorrer crash ou comportamento inesperado, **interromper**, não insistir.

### Escopo permanente

A dublagem está **COMPLETAMENTE FORA DO PROJETO** até tradução PT-BR/ES/EN integralmente correta, seletor funcional e gameplay/saves/estrela→castelo aprovados no Xbox e nova autorização explícita.

**TEST9 É CANDIDATO EXPERIMENTAL, NÃO RELEASE.**
