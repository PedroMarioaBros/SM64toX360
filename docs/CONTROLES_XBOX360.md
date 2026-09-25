# Super Mario 64 PT-BR — controles do port para Xbox 360

Mapeamento da compilação `sm64corrigido.xex`, preservado na tradução 0.4. Foi obtido das instruções do executável e conferido com entradas controladas.

| Controle Xbox 360 | Ação no jogo | Entrada interna |
|---|---|---|
| Analógico esquerdo | Mover Mario; mirar canhão; olhar em câmera próxima | Analógico N64 |
| A | Pular, nadar, disparar canhão; avançar diálogos | A N64 |
| X | Atacar, conversar, placas, pegar/arremessar; diálogos | B N64 |
| LT ou LB | Agachar; Bundada; modificador de saltos | Z N64 |
| RB ou RT | Alternar câmera Lakitu/Mario; segurar câmera fixa | R N64 |
| Analógico direito ←/→ | Girar câmera | C-esquerda/direita |
| Analógico direito ↑ | Aproximar/olhar ao redor | C-cima |
| Analógico direito ↓ | Afastar visão | C-baixo |
| START | Iniciar/pausa conforme tela | START N64 |
| Direcional | Direções digitais | D-pad N64 |

Combinações úteis: Salto Longo = correr + LT/LB + A; Mortal para Trás = parado + LT/LB + A; Bundada = no ar LT/LB; chute = A depois X; canhão = mirar no analógico esquerdo e A; Bowser = X na cauda, girar analógico esquerdo e soltar X.

## Outros botões nessa compilação

- B: não produz botão de jogo na rotina examinada.
- cliques dos analógicos: não produzem botão de jogo.
- BACK sozinho: não produz botão de jogo.
- Y: alterna a depuração gráfica `skipdecals`.
- BACK + START: solicita diagnóstico gráfico.

A versão 0.4 não altera essas funções.

## Evidência técnica

Wrapper de leitura: `0x8239E010`; import `XamInputGetState`, ordinal `0x191`; mapeador `0x82165998`–`0x82165C90`. SHA-256 dos bytes do mapeador: `b51af5c7f53d6cf7a058a3353f9de40dfbe514890a0822427c151026904d3e03`.

Limiares encontrados: LT/RT >64/255; câmera no analógico direito acima de +16000 ou abaixo de −16000; deadzone do analógico esquerdo 7849, depois divisão por 256 e limite −128..127. Y e BACK+START usam detecção de novo pressionamento.