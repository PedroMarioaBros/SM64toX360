# Manifesto forense — linha Native60 recuperada

Data da recuperação: 25/09/2026.

A limitação de materialização da Biblioteca foi contornada sem alterar os
originais: cópias técnicas temporárias permitiram recuperar os byte streams,
recomputar hashes e extrair os relatórios internos dos ZIPs.

## Artefatos recuperados

| Build | Estado dos bytes | Identidade |
|---|---|---|
| v0.5 DIAG 60HZ DUPLICADO | XEX + ZIP recuperados | hashes recomputados |
| v0.6 INTERPOLADO Y 30/60 | XEX + ZIP recuperados | hashes recomputados |
| v0.7 NATIVE60 CORE | XEX + ZIP recuperados | reconstrução XEX exata |
| v0.8 RETIME CORE A | XEX + ZIP recuperados | reconstrução XEX exata |
| v0.9 FINAL60 RC1 | XEX + ZIP recuperados | reconstrução XEX exata |
| v0.10 NATIVE60 RC2 | XEX + ZIP recuperados | reconstrução XEX exata |

## Evolução arquitetural

**v0.5** validou um segundo present visual sem segunda lógica.  
**v0.6** adicionou interpolação de matrizes e alternância Y 30/60; foi uma linha experimental.  
**v0.7** descartou duplicação/interpolação e mudou o loop inteiro para ~60 Hz.  
**v0.8** iniciou retiming de física/áudio.  
**v0.9** ampliou retiming por code cave.  
**v0.10** corrigiu o mapeamento shell/walking e retimou subsistemas ainda acelerados.

## Prova de reconstrução

A v0.4 já havia sido reconstruída com XEX idêntico. Nesta retomada:
- v0.7 reconstruída = original;
- v0.8 reconstruída = original;
- v0.9 reconstruída = original;
- v0.10 reconstruída = original.

Portanto a cadeia binária crítica do projeto deixou de depender do histórico do
chat: seus patches essenciais estão preservados como código reexecutável no GitHub.
