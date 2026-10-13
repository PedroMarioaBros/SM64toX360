# SM64 Xbox 360 — curso/estrelas trilíngues prontos para ligação ao seletor

## Descoberta binária real — TEST3 aprovado em hardware

A cópia intacta da TEST3 que Pedro aprovou para o ciclo **fase → pegar estrela → castelo** foi descriptografada localmente, **somente para leitura**, para sua imagem PE mapeada.

- XEX SHA-256: `b90ae1d1be953c1f817e9c64286c67da855778ac7c671098a3cd8495d8b6afd9`;
- PE mapeado SHA-256: `a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c`;
- Tabela de nomes de cursos: **offset de imagem** `0x009E8C70`, endereço VA `0x829E8C70`, exatamente **26 ponteiros BE de 32 bits**. SHA-256 dos 104 bytes: `3b789baca2d6d547c0f8f2985e96da24b4878944c1278d092c614d53934cbc9d`;
- Tabela de nomes de estrelas: **offset de imagem** `0x009E9620`, endereço VA `0x829E9620`, exatamente **90 ponteiros BE de 32 bits**. SHA-256 dos 360 bytes: `ed5c7e598cade70bcfda05d3293b230a449650f9b45bf1f52572749640be30b0`;
- **Todos os 116 ponteiros se referem a endereços dentro do mapeamento real TEST3.** Os 26 ponteiros de área são distintos; as 90 estrelas usam 89 textos físicos distintos (uma string é reaproveitada);
- Índices de cursos 0–14: 15 fases principais, por ordem `COURSE_BOB,WF,JRB,CCM,BBH,HMC,LLL,SSL,DDD,SL,WDW,TTM,THI,TTC,RR`;
- Índices 15–24: as 10 posições de `SECRET_STAR`, inclusive `COURSE_CAKE_END` com nome vazio (índice 24 da tabela aponta a recurso nativo); índice 25 `CASTLE_SECRET_STARS`;
- Os 90 nomes de estrelas são precisamente os 15 cursos x 6 atos na ordem do motor, incluindo a missão PT-BR **Detonando a Parede** (COURSE_WF, sexta estrela).
- **Não confundir offsets de arquivo PE mapeado com offset físico do arquivo XEX criptografado.**

## Código de integração segura

`scripts/multilang/install_trilingual_course_tables.py`:

1. Recebe um PE **já preparado com a seção `.lang`** `SM64LANG` no RVA `0x01040000`, capacidade `0x20000`, mais `_localization_build/{en,es}/course_catalog.json`;
2. Confere byte a byte via SHA-256 as 26+90 referências PT-BR da TEST3 **antes de qualquer gravação**. Se os offsets/hash não coincidirem, aborta; não ajusta silenciosamente a base;
3. Reserva metadados **COURSE3** nos bytes `0x80..0xB3` do header `.lang`, onde o antigo `build_lang_section.py` não tem outros dados. Os ponteiros dos 170 diálogos e textos pré-existentes não são movidos;
4. Copia os ponteiros PT-BR originais como estão, **sem reescrever seus textos**;
5. Codifica nomes EN/ES e cria três tabelas 26×4B e três tabelas 90×4B, preservando a posição vazia do curso especial 24;
6. Não modifica um byte sequer abaixo de `LANG_RVA` nem injeta código/gancho de execução. Um check de região compara `result[:LANG_RVA]` com a entrada.
7. O script de build recusa metadados ocupados, bytes não vazios além do cursor, curso fora da ordem nativa, nomes inesperadamente vazios, falta de espaço ou hash da TEST3 alterado.

**Limite:** esta etapa gera estrutura de dados e metadados `COURSE3`, **não executável final**. Ela ainda precisa receber um PE `.lang` compatível e ser ligada à seleção no título.

## Rotina PowerPC de ativação independente

`scripts/multilang/course_table_activation.py`:

- Endereço proposto de rotina isolada: `0x823BCC00` (região testada vazia no PE TEST3, não instalada no Xbox);
- Interface: r3 = 0 PT, 1 ES, 2 EN; entradas inválidas voltam ao PT;
- Lê offsets das tabelas COURSE3 em `0x83040098` (cursos) e `0x830400A4` (estrelas);
- Copia exatamente 26 e 90 ponteiros de nomes às tabelas globais originais `0x829E8C70` e `0x829E9620`;
- PPC Big Endian de **148 bytes**, SHA-256 `f7cd86fb68725d8aa6f4c6fb5d9c9de7274434fa48f9d19368b3c78edb40d67b`;
- **Não altera hook de `level_script_execute` em `0x820CD128`** e não é instalado no XEX nesta fase.

## Testes reais de CI

- [Trilingual Xbox Course Table Staging — run 38334053320](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334053320): **7 testes PASS** com dados sintéticos. Validação de 26/90 tabelas, proteção PT-BR, metadados e ausência de alterações fora de `.lang`.
- [Xbox Trilingual Course Activation PPC — run 38334216661](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38334216661): **PowerPC Unicorn emulado PASS**. Exercitou PT/ES/EN e seletores inválidos 99 e -1; foram copiados 26+90 ponteiros nos destinos corretos em todos os cinco casos sem sobrescrever sentinelas adjacentes.
- **Nenhum teste acima equivale a boot, menu ou jogabilidade no hardware Xbox 360.**
- Assets originais, ROM, XEX, tradução textual de terceiros e conteúdo de áudio permanecem fora do GitHub público.

## Próxima tarefa: transformação em compilação jogável

1. Reaproveitar `build_dialog_pools.py` e o build `.lang` com o **PE original TEST3** e o charmap/glyph espanhol validado. Confirmar que `pt_br` continua byte-idêntico.
2. Aplicar `install_trilingual_course_tables.py` à `.lang` e conferir meta `COURSE3` e offsets PT/ES/EN em um **PE real não sintético**, com integridade/assinatura XEX posteriormente.
3. Ligar rotina original de 170 diálogos `language_activation.py` e a nova rotina 26+90 nomes **somente** a um seletor dentro de `intro_regular/lvl_intro_update` (tela normal de título pós-créditos); nunca restaurar o hook geral de `level_script_execute`.
4. Traduzir e integrar UI/menus que não estão nessas duas famílias de tabelas. Auditar semanticamente ES comparado a PT e EN.
5. Construir XEX candidato 30 FPS com hashes e validação local de ida/volta do PE e testar **os três idiomas** no Xbox: boot → seletor → diálogos/placas/fases/estrelas → saída de fase → castelo → saves.
6. **Vozes/dublagem continuam fora do escopo conforme pedido.**

**Estado exato:** mapeamento de tabelas proveniente de TEST3 real; rotina PPC emulada; catálogo multilíngue **ainda não está instalado/ativo no jogo**, nenhum novo XEX entregue.
