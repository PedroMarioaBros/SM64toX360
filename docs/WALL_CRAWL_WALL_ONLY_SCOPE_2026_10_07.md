# Wall-crawl — escopo inicial somente para paredes verticais

## Decisão

A primeira implementação do crawling será limitada a paredes verticais. Tetos,
paredes inclinadas e transições entre superfícies ficam fora deste protótipo.

## Comportamento desejado

1. Mario encosta numa parede e entra na pose normal de mãos apoiadas.
2. Enquanto o botão de agachar/engatinhar estiver pressionado, e somente nesse
   estado de contato, ele adere à parede.
3. O analógico esquerdo controla o deslocamento na parede: cima sobe, baixo
   desce, esquerda/direita percorrem lateralmente.
4. O analógico direito continua exclusivamente controlando a câmera.
5. Ao soltar o botão de agachar/engatinhar, Mario sai do estado aderido e usa a
   queda normal; não há permanência artificial na parede.
6. Pulo A/B/Y, câmera, menu, saves, PT-BR e 30 FPS permanecem intocados.

## Contrato técnico mínimo

- Pré-condição: `m->wall != NULL`, Mario em estado de mãos na parede e botão de
  agachar pressionado.
- A normal da parede deve ser lida do mesmo `Surface` que já alimenta
  `push_or_sidle_wall()`.
- Para o protótipo vertical, a normal deve ter componente Y próxima de zero;
  contatos inclinados são rejeitados e seguem a física original.
- O vetor do analógico é convertido para deslocamento no plano da parede,
  mantendo o eixo vertical do mundo para subir/descer.
- A posição deve ser reencostada na parede após o passo, com tolerância finita,
  e a colisão deve ser reavaliada a cada quadro.
- Se a parede desaparecer, o botão for solto ou a colisão falhar, retornar à
  ação de queda/crawling original.

## Critérios de aceitação no Xbox

- Encostar numa parede sem pressionar o botão continua exatamente igual.
- Segurar o botão na parede permite subir e descer com o analógico esquerdo.
- Soltar o botão faz Mario cair sem travar ou ficar flutuando.
- Analógico direito não causa salto nem crawling.
- Entrar numa parede inclinada não ativa o protótipo e não altera a física.
- Depois de coletar estrela e retornar ao castelo, o menu de salvar continua
  funcional.

## Estado atual

Este documento é especificação; nenhum XEX foi alterado. A análise PE ainda não
localizou uma função/ABI segura para o patch. O próximo passo é cross-reference
por fluxo de registradores e chamadas de colisão, seguido de um harness estático
do contrato antes de gerar qualquer executável.
