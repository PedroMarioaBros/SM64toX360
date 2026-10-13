# Localização trilíngue — Super Mario 64 Xbox 360

Edição única planejada com **Português, Español, English** e **controles Xbox 360 em todos os idiomas**. Os textos traduzidos devem comunicar a mesma informação, sem introduzir novos comandos, retirar instruções ou alterar o conteúdo das fases.

## Regra de preservação

- **PT-BR**: a tradução da PMCN Studios aprovada no Xbox 360 é a fonte canônica, sem importação de uma tradução brasileira externa nem alteração de bytes de seus diálogos.
- **EN**: fonte original US do SM64 (pinned `n64decomp/sm64`), com adaptação **apenas das referências aos controles** do console.
- **ES**: fonte `Reonu/ultrasm64-spanish`, com alinhamento dos 170 IDs, correção explícita de omissões técnicas e dos nomes de missões. Fonte é espanhol da Espanha; revisão editorial para manter o mesmo significado continua necessária.
- **Vozes**: adiar integração das novas dublagens por decisão do proprietário. Inglês nativo permanece.

## O que já é reproduzível sem ROM ou XEX

`scripts/multilang/import_text_sources.py`: importa 170 diálogos EN e 170 ES do código-fonte fixado.

`scripts/multilang/localize_controller_texts.py en` e `... es`: localiza ações de Xbox, sem deixar tokens N64, e executa as erratas ES verificadas.

`scripts/multilang/audit_language_parity.py`: verifica IDs e presença de todas as categorias de comandos Xbox nos diálogos; **não garante equivalência literária completa**.

`scripts/multilang/import_course_catalog.py`: constrói EN/ES 15 fases × 6 missões, 10 posições secretas, textos de castelo e auxiliares, com IDs iguais.

CI validada em [18 testes e corpus real, 12/10/2026](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38333296556).

Relatório completo: [docs/TRILINGUAL_TEXT_PARITY_2026_10_12.md](../docs/TRILINGUAL_TEXT_PARITY_2026_10_12.md).

## Ainda não é uma versão multilíngue jogável

A geração dos corpora e dos catálogos **não** ativa a escolha de idioma no XEX. Faltam integração de menus/cursos, revisão de significado dos textos, seletor seguro e teste real em três idiomas.

A versão TEST3 de 30 FPS passou o teste de estrela→castelo no Xbox. A tentativa posterior de créditos pelo hook global de `level_script_execute` falhou; não reutilizar esse hook como seletor.

Nenhum ROM, XEX, WAV, dados de jogo completos ou grandes trechos de fontes externas são distribuídos por este repositório público.
