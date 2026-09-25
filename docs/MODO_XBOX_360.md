# Modo Xbox 360 — especificação consolidada

## Decisões consolidadas

- O jogo base inicia fiel ao clássico em **30 FPS**, com localização PT-BR e controles Xbox 360.
- Todos os extras ficam no menu aberto por **Back/Select**, chamado **Modo Xbox 360**.
- A opção **60 FPS** pertence a esse menu; a decisão anterior de 60 FPS permanente foi substituída.
- Três modos de câmera devem coexistir: **Lakitu → Mario → Xbox**.
- No modo Xbox: analógico esquerdo move Mario; analógico direito controla câmera livre horizontal/vertical; movimento é relativo à câmera e a física original de Mario deve ser preservada.
- A câmera moderna deve prever deadzone, suavização e tratamento de colisão/obstrução; câmeras especiais/cutscenes podem assumir temporariamente e o jogo retorna ao modo Xbox ao terminar.
- Um símbolo/ícone Xbox identifica o terceiro modo.
- O seletor de idioma é a exceção fora do menu: antes do Start, **English / Español / Português**, aplicando o idioma ao jogo inteiro.
- O programa de extras registrado inclui Wing/Metal/Vanish, casco Koopa, itens sem expiração, magnetismo de itens, invencibilidade com efeito de estrela, Fire Mario/bolas de fogo, novos power-ups, Luigi jogável com física própria e melhorias gráficas/texturas HD/upscaling. Esses itens devem ser avaliados/implementados um por vez; nenhum deles é tratado aqui como já implementado.

## Botões B e Y

Na base 0.4 recuperada, **B isolado não envia ação de jogo** na rotina examinada; **Y alterna `skipdecals`** (diagnóstico) e Back+Start solicita diagnóstico gráfico. Durante a v0.6, Y também foi usado temporariamente para alternar 30/60 FPS. O projeto posterior determinou não depender desse uso temporário de Y para a interface final.

A ideia de usar **B para executar diretamente o terceiro pulo** foi registrada como proposta de jogabilidade, mas não há evidência de implementação. Deve permanecer classificada como proposta até decisão/implementação explícita.

## Não implementado

Não foi recuperado XEX que comprove a implementação do menu Modo Xbox 360, da câmera livre, do seletor trilíngue, Luigi, novos power-ups ou melhorias HD. Esta documentação preserva decisões de design, não transforma planejamento em funcionalidade existente.