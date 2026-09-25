# Status atual

## Comprovado por bytes recuperados

- `sm64corrigido.xex`: base corrigida, SHA-256 `6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8`.
- `sm64-ptbr-teste.xex`: versão 0.4, SHA-256 `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`.
- pacote 0.3 e pacote 0.4.
- checkpoint completo de 17/09/2026, contendo scripts, imagens mapeadas, disassemblies, documentação e projeto 0.4.
- quatro fotos dos menus usadas no diagnóstico visual.

## Existência comprovada na Biblioteca, bytes indisponíveis na auditoria

As v0.5, v0.6, v0.7, v0.8, v0.9 e v0.10 possuem entradas XEX e ZIP reais com tamanho/data. O armazenamento recusou materialização raw desses Project files. Isso é diferente de “arquivo inexistente”: eles foram localizados, porém não entraram no ZIP de migração como binários originais.

## Estado de teste

- 0.3: teste de save/load e “Salvar e sair” confirmado no histórico e citado no LEIA-ME da 0.4.
- 0.4: documentação posterior registra relato do usuário de que funcionou no Xbox.
- v0.9: última versão 60 FPS com feedback de hardware encontrado.
- v0.10: última versão produzida; teste posterior não encontrado.

## Pendências imediatas

1. Recuperar/testar a v0.10 RC2 no Xbox 360 caso o byte stream original volte a ficar acessível.
2. Validar os pontos específicos listados em `PONTO_DE_RETOMADA.md`.
3. Só depois decidir quais correções da RC2 entram na futura opção 60 FPS do Modo Xbox 360, mantendo 30 FPS como padrão canônico.
4. Não publicar XEXs/ZIPs/artefatos derivados no GitHub público sem revisão de direitos.