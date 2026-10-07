# Projeto de locomoção aderida — 07/10/2026

Requisito: enquanto Mario tocar uma superfície e mantiver o botão de engatinhar/abaixar, aderir e mover-se com o analógico esquerdo em qualquer direção, inclusive paredes, inclinações e teto. Ao soltar, retornar à física original.

Estado: não implementado/testado. Plano: localizar ação de contato/empurrão, normal de colisão e ABI; criar estado de aderência; projetar o analógico no plano tangente da normal; manter colisão; testar parede, inclinação, teto, soltura, quedas e wall-kick. Não gerar XEX antes da confirmação estática. Preservar base 30 FPS, A/B/Y, câmera, menu/save e PT-BR.