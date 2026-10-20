# Diagnóstico estático: seletor confirma idioma, mas a interface não muda — 20/10/2026

## Resultado confirmado pelo proprietário
No Xbox 360 físico, TEST11 inicia, mostra créditos, permite percorrer Português / Español / English e confirma com A. Depois da confirmação, a tela seguinte ainda mostra “APERTE START” em português. Não foi relatado crash nessa sequência.

## Evidência no código versionado
1. `scripts/multilang/pregame_gate.py` guarda o idioma escolhido em `.lang + 0x18` e, ao confirmar, passa esse valor em r3 para `ACTIVATE_LANGUAGE = 0x823BC800`. Em seguida muda o estado do gate para 2, que deixa o fluxo voltar ao `level_script_execute` original.
2. `scripts/multilang/language_activation.py` implementa somente a cópia de 170 ponteiros de texto para os registros de diálogo canônicos em `0x829E7CD8`. Os testes em Unicorn verificam esses 170 ponteiros, não os textos da tela de título nem os rótulos do menu de saves.
3. `scripts/multilang/build_lang_section.py` coloca na seção `.lang` as três tabelas/pools de diálogo e textos próprios do seletor/créditos. O array `selector_texts` contém o texto de apresentação do seletor, mas não define strings localizadas para “APERTE START”/“PRESS START” nem para os rótulos de save.
4. Portanto, os testes estáticos existentes comprovam a escolha e a troca da tabela de diálogos, mas **não comprovam que a tela de título ou o menu de saves consultem o idioma selecionado**. O relato físico é coerente com essa lacuna. Não há evidência suficiente para culpar a navegação do seletor nem para afirmar que a ativação dos 170 diálogos falhou.
5. A fonte pública de referência separa esses caminhos: `title_screen.c` chama `print_intro_text()` para a tela Press Start, enquanto `file_select.h`/a rotina de renderização do menu de arquivos trata os textos do file-select separadamente. Isso serve como mapa conceitual; não fornece endereços transferíveis para o XEX Xbox 360.

Referências públicas conceituais:
- https://github.com/n64decomp/sm64/blob/master/src/menu/title_screen.c
- https://github.com/n64decomp/sm64/blob/master/src/menu/file_select.h

## Conclusão
A próxima falha a resolver não é mais “fazer o cursor funcionar”. É ligar o estado de idioma a cada sistema de texto real do port: primeiro o prompt Press Start/título; depois os menus de saves/opções; depois nomes de cursos e demais textos. A tabela de 170 diálogos deve ser preservada e testada separadamente.

## Próxima ação segura
Fazer varredura do PE privado TEST11/base v0.4 para localizar os textos nativos e as rotinas de renderização correspondentes, usando somente bytes recuperados e referências cruzadas reais. Em seguida documentar endereços, formato de texto, limites de espaço e um teste estático fail-closed antes de modificar qualquer byte. Não aplicar endereços da versão N64/MIPS nem fazer patch especulativo. Não gerar uma nova build para o console até existir evidência estática verificável.

## Limites desta etapa
- Análise estática dos scripts versionados + relato de teste físico do proprietário.
- Nenhum PE/XEX foi alterado ou gerado nesta etapa.
- Nenhum novo teste de Xenia ou de hardware foi executado nesta etapa.
- TEST11 continua referência de navegação no Xbox físico, não uma edição trilíngue concluída.
- Dublagem continua fora do escopo.
