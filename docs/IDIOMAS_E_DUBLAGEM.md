# Idiomas e dublagem — plano da edição multilíngue

Branch de desenvolvimento: `feature/multilang-dub-30fps`.

## Escopo real de partida

A base de trabalho NÃO começa do zero.

Já existe no jogo:
- port Xbox 360 com cannon fix;
- tradução PT-BR funcional;
- localização das instruções/placas dos comandos de Nintendo 64 para Xbox 360;
- saves e demais comportamentos preservados;
- base canônica de 30 FPS.

A linha Native60 permanece separada até validação posterior em hardware.

## Resultado desejado

Antes de qualquer tela original do jogo, a edição deverá oferecer:

**Português · Español · English**

Cada opção aparece escrita no próprio idioma.

A seleção define, em conjunto:
1. textos;
2. nomes de fases/estrelas;
3. menus;
4. placas e instruções de controle;
5. vozes/falas;
6. créditos específicos da localização usada.

## Português

Usar a tradução/localização PT-BR já existente no nosso jogo como fonte principal.

Adicionar somente o que falta:
- banco de vozes PT-BR compatível;
- mapeamento das falas para os eventos originais;
- créditos dos dubladores/projeto de origem.

Referência localizada:
- https://github.com/bMatSantos/sm64-ptbr

Esse projeto credita BMatSantos e Kosmus na tradução e Vihh_Art como Peach. O repositório não declara licença própria para essas contribuições, portanto a integração deve separar análise técnica de redistribuição pública dos arquivos.

## Español

Criar a localização espanhola sobre a mesma base Xbox 360:
- diálogos;
- HUD/menus;
- nomes;
- placas;
- instruções de controle adaptadas para Xbox 360;
- banco de vozes em espanhol.

Referências localizadas:
- https://github.com/Reonu/ultrasm64-spanish
- projeto comunitário “Habla Mario 64 v3 — Textos y Voces en Español”.

A publicação do Habla Mario 64 v3 credita, entre outros:
- tradução: Rigbound, Noobazo, Madnyle, Tamakii, YeyoKermit, AlexPoggers, Mario Produ e AlexBlue150;
- vozes: Madnyle (Mario) e Jess (Peach).

## English

Manter:
- textos originais em inglês;
- vozes originais em inglês;
- comportamento original do port.

Não traduzir nem reinterpretar o conteúdo inglês.

## Regras de integração

- Um único jogo/executável.
- Idioma selecionado controla texto + voz.
- Não duplicar lógica de gameplay por idioma.
- Não alterar formato do save do SM64 sem necessidade.
- Preferir configuração de idioma separada do save principal.
- Preservar cannon fix e controles Xbox 360.
- Não introduzir dependência dos 60 FPS nesta fase.
- Todo asset externo deve ter origem e crédito documentados.

## Próxima etapa técnica

1. Inventariar todos os pontos de texto da build atual.
2. Inventariar todos os IDs/eventos de voz usados pelo port.
3. Comparar esses IDs com os bancos PT-BR e espanhol.
4. Construir tabela canônica `evento -> pt_br / es / en`.
5. Implementar carregamento/seleção por idioma.
6. Inserir tela inicial de créditos + seletor.
7. Gerar build 30 FPS de teste para Xbox 360.
