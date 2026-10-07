# Projeto de locomoção aderida — 07/10/2026

## Requisito confirmado
Enquanto Mario estiver em contato com uma superfície e mantiver o botão de engatinhar/abaixar pressionado, ele deve aderir à superfície e se mover com o analógico esquerdo em qualquer direção. A mesma regra deve funcionar em parede vertical, parede inclinada, teto e demais superfícies válidas. Ao soltar o botão, a aderência termina e a física decide entre permanecer apoiado ou cair.

## Estado atual
Ainda não implementado e não testado no Xbox 360. A base aprovada continua sendo a v0.4/30 FPS com pulos A/B/Y, câmera no analógico direito, menu/save e textos PT-BR preservados.

## Plano técnico obrigatório
1. Localizar no XEX a ação de contato/empurrão na parede e a rotina de detecção de colisão que fornece a normal da superfície.
2. Confirmar o contrato de atualização de posição/velocidade e a representação de ação, sem reutilizar o endereço rejeitado do seletor (0x820D5F48).
3. Criar estado de aderência separado: entrada = contato + botão de engatinhar; saída = soltura, perda de contato ou transição explícita.
4. Projetar o vetor do analógico esquerdo no plano tangente da normal: v_t = v - normal * dot(v, normal), com orientação estável para paredes, inclinações e teto.
5. Atualizar posição/orientação e manter colisão; testar primeiro em cenário controlado, depois em superfícies inclinadas e teto.
6. Ao soltar, restaurar a física original e testar quedas, aterrissagem, wall-kick e save/menu.

Nenhum XEX deve ser gerado antes da confirmação estática dos endereços e do ABI.
