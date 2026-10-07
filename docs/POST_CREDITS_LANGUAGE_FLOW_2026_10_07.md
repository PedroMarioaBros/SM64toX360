# Fluxo multilíngue pós-créditos — decisão de arquitetura

Data: 07/10/2026
Branch: feature/multilang-dub-30fps

## Fluxo aprovado

1. Créditos universais originais do jogo, sem seletor anterior.
2. Tela original equivalente a “Aperte Start” passa a mostrar Português, Español e English.
3. Direcional cima/baixo movimenta a seleção; A confirma.
4. A confirmação ativa a tabela de 170 diálogos do idioma escolhido.
5. Antes do menu de saves, aparece uma tela/painel de créditos personalizados no idioma escolhido.
6. A confirma os créditos personalizados e continua para o menu normal de arquivos/saves.
7. O fluxo original de seleção de save e entrada no jogo permanece intacto.

## Créditos personalizados

A tela deve creditar o jogo original e a Nintendo, o port para Xbox 360, a localização/tradução, futuras dublagens e PeterKleizoon — PMCN Studios. Nomes próprios e marcas não devem ser traduzidos de forma inadequada.

## Restrições

- Base canônica 30 FPS; não misturar Native60.
- Preservar PT-BR, pulos A/B/Y, câmera, menu e saves já aprovados.
- Remover o caminho de seletor antes dos créditos; não usar o hook pré-créditos como solução.
- Não alterar o menu de saves além da tela de créditos/painel anterior.
- Se a seleção não for persistida, ela será refeita no próximo boot.

## Próxima implementação

Mapear a rotina original intro_regular/lvl_intro_update no XEX e inserir o seletor no fluxo pós-créditos. Validar primeiro a tela e a confirmação sem ativação; depois ativar os 170 ponteiros; por fim inserir os créditos personalizados multilíngues.

Nenhum executável desta arquitetura foi gerado ainda.
