# Levantamento estático — crawling em superfícies — 07/10/2026

## Evidência encontrada na fonte recuperada
- `act_standing_against_wall()` em `src/game/mario_actions_stationary.c`: mantém Mario na animação de mãos na parede e atualmente sai quando há analógico, A, perda do chão ou início de escorregão.
- `push_or_sidle_wall()` em `src/game/mario_actions_moving.c`: recebe `m->wall`, lê `m->wall->normal`, calcula o ângulo da parede e escolhe a animação `MARIO_ANIM_PUSHING`/sidestep. É o ponto lógico que detecta o contato com a parede durante o movimento.
- `act_crawling()` em `src/game/mario_actions_moving.c`: já usa `INPUT_Z_DOWN`, analógico esquerdo, `update_walking_speed()`, `perform_ground_step()` e `align_with_floor()`. A nova ação deve reutilizar a intenção de movimento, mas substituir o passo no chão por passo aderido à superfície.
- `WallCollisionData` em `src/engine/surface_collision.h`: `find_wall_collisions()` fornece até quatro paredes em `walls[]`; `struct Surface` fornece a normal usada pelo motor.
- `ACT_STANDING_AGAINST_WALL` = `0x0C400209`, `ACT_START_CRAWLING` = `0x0C008223`, `ACT_STOP_CRAWLING` = `0x0C008224`, `ACT_CRAWLING` = `0x04008448` na fonte recuperada. Esses são IDs de ação, não endereços do XEX.

## Interpretação para a implementação solicitada
1. Ao estar em `ACT_STANDING_AGAINST_WALL` e detectar o botão de engatinhar, entrar em uma ação nova de aderência, sem alterar a ação de crawling normal do chão.
2. Guardar a normal da superfície e recalcular o contato a cada quadro.
3. Projetar o vetor do analógico no plano tangente da normal, mantendo a componente normal apenas para conservar a distância de contato.
4. Usar a normal da superfície para orientar o modelo; não limitar a normal a paredes verticais, para incluir inclinações e teto.
5. Ao soltar o botão ou perder contato, sair para a física original apropriada.

## Bloqueio técnico atual
A fonte identifica os pontos lógicos, mas os endereços/ABI correspondentes no PE/XEX ainda precisam ser confirmados por cross-reference. Portanto, nenhum executável foi alterado ou liberado nesta etapa.
