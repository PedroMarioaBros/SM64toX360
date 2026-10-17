# TEST5 reprovada em Xbox 360 — relatório de regressão (17/10/2026)

## Observação em hardware do proprietário (não inferência)
O jogo abre, executa créditos iniciais, mostra a tela normal de **Aperte Start**, abre o menu de saves e entra no jogo PT-BR. **O seletor Português / Español / English continua completamente ausente**, exatamente como na TEST4.

- TEST3: aprovado anteriormente para entrada em fase, coleta de estrela e retorno ao castelo.
- TEST4: boot/saves/PT-BR parcial PASS, seletor FAIL (testado no console).
- **TEST5: boot/saves/PT-BR parcial PASS, seletor FAIL (testado no console).**
- Não houve teste reportado de estrela→castelo na TEST5. Não classificar TEST5 como estável.
- A dublagem continua estritamente FORA DO ESCOPO.

## Reabertura da investigação: afirmações anteriores não comprovavam execução real
A alegação anterior de que trocar a BL de `0x820D68BC` para `0x82147448` resolveria a seleção foi **prematura**: apenas os pontos de chamada e bytes estáticos foram verificados, e os testes CPU começavam diretamente pelo wrapper, **não pelo ciclo de boot do jogo**. Não repetir uma terceira compilação com a mesma abordagem sem distinguir se o código roda em hardware ou se seu desenho falha.

## Inspeção REAL do PE mapeado TEST3, TEST4 e TEST5 (decriptografia local somente para análise)
Hashes SHA-256 confirmados:
- TEST3 PE: `a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c`;
- TEST4 PE: `10549edf9a516b6b7099034519ea5973ed0ad989042d7a25a5b74155a1f729e1`;
- TEST5 PE: `a6c0a1c451f6dd114f73bd324cb297d42f3ed6f6c027c8237d3244284e622672`.

Evidências:
1. TEST5 realmente contém a BL alterada `482754b9` no offset da imagem `0x147448`, enquanto TEST3/TEST4 contêm `4bfffe31` ali.
2. TEST5 realmente contém o wrapper PPC no offset de imagem `0x3BC900` (`7c0802a6 9421ff60...`).
3. Em TODAS as TEST3/4/5, `.lang+0x14` (estado da seleção) está inicializado a **zero** e `.lang+0x18` (índice) a zero. Portanto, **um estado inicial 1 no arquivo NÃO explica o bypass**; eventual inicialização em runtime continua sem observação.
4. Os scripts da tela original contêm callbacks apontando para `0x82147408`; em `0x82147448` existe a BL para intro_regular da tela comum. Porém ter essa BL no arquivo **não comprova** que a sequência de hardware esteja executando este caso, nem que renderizador seja compatível.
5. Se o wrapper em `0x823BC900` for executado com estado 0, seu código retorna 0 e suprime Start. O fato de o Start continuar funcionando implica que a lógica não está controlando o fluxo observado. Causas ainda em aberto: callback ou estado real diferente; dados/carregamento do arquivo efetivamente executado, tratamento de intro alternativo; dependências de renderização não modeladas.
6. O patch literal de título terá que atuar como marcador independente para provar que o binário atualizado está sendo carregado, sem depender do código do seletor.
7. O único estado de XEX estável comprovado em transição estrela→castelo continua TEST3.

## Próxima ação baseada em prova, não suposição
**Não promover a TEST5.** Criar TEST6 estritamente DIAGNÓSTICA a partir de TEST5 (se necessário), com um identificador visual *direto nas duas strings ASCII conhecidas do texto de abertura* (sem alterar código, controles, idioma, save ou hook). Se a marca não aparecer, há diferença no recurso realmente desenhado ou no executável em execução. Se aparecer, o jogo carrega dados novos mas o callback/gate da seleção não está controlando o título. Interpretar ambos os resultados antes de mudar o código do seletor novamente.

Não confundir uma troca de texto simples com uma implementação do seletor. O objetivo continua PT/ES/EN com controles Xbox e equivalência de conteúdo, com tela de seleção funcional e gameplay estável antes de reabrir qualquer trabalho com dublagem.
