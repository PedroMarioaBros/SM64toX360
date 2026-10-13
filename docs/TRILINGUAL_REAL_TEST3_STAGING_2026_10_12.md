# Teste real de integração multilíngue sobre a TEST3 — 12/10/2026

## Resultado verificável (não é ainda um XEX jogável)

**O PE mapeado derivado do XEX TEST3 que Pedro aprovou em hardware foi modificado somente dentro da seção de dados `.lang`.** A TEST3 aprovada continua intacta em seu ZIP original e na Biblioteca privada.

| Item | Resultado |
|---|---|
| Base mapeada TEST3 SHA-256 | `a1bc5c6db7e32d4214c2d1329874f68dee058c91063b67bbacde7ae197a48f6c` |
| Módulo após cursos/missões, antes de delta de diálogos | `aaa20fde15ed991ecee8c9af4b4f03e69b299fcb9e193065303f5f5dfc616be9` |
| PE após tabelas **e** correções ES | `96abbfb76775f4184b24106c1b78a1409ac1d9ace8bf5fa61a98af76a1b9eed8` |
| Tamanho PE | 17.170.432 bytes |
| Nomes de áreas por idioma | 26 (PT-BR / ES / EN = 78 ponteiros) |
| Nomes de estrelas por idioma | 90 (PT-BR / ES / EN = 270 ponteiros) |
| Diálogos PT-BR | 170 — **nenhum ponteiro/string alterado** |
| Diálogos EN | 170 — **nenhum ponteiro alterado** |
| Diálogos ES | 170 — **20 textos/pointers atualizados seletivamente** |
| Bytes de `.lang` disponíveis depois da integração | **13.841 / 131.072** |
| Código fora da seção `.lang` | **100% igual à TEST3** |
| Hook global de `level_script_execute` | `4bfc8321` (original e intocado) |
| Hook anterior da intro `0x820D5F48` | Original e intocado |

IDs dos 20 diálogos ES corrigidos: **015, 030, 032, 033, 034, 035, 042, 046, 049, 051, 054, 060, 064, 065, 066, 074, 105, 131, 149 e 163**. A rotina verificou que cada string EN/ES, após a codificação real do SM64, corresponde byte a byte à fonte preparada e formatada dentro dos novos ponteiros.

A verificação independente conferiu **todos os 510 ponteiros dos diálogos** e **todos os 348 ponteiros de cursos/estrelas**, incluindo os textos especiais vazios válidos. Os 170 ponteiros PT-BR e o pool de textos PT-BR são byte-idênticos aos da TEST3; todas as tabelas PT-BR de áreas/estrelas permanecem byte-idênticas. Nenhuma string ou código da tradução do proprietário foi substituído.

### Erro de integração real encontrado e corrigido

A primeira execução contra o PE real falhou com `extra labels are not aligned`. Causa: a serialização de `course_catalog.json` transforma índices numéricos `0..6` de `EXTRA_TEXT` em chaves JSON string `"0".."6"`. A auditoria de objetos Python em memória passava, mas a auditoria do catálogo serializado real falhava.

Corrigido `scripts/multilang/import_course_catalog.py` para normalizar os sete índices antes da comparação, sem relaxar sua sequência esperada nem permitir entradas faltantes. Novo teste de ida e volta JSON incorporado. Após correção, o staging em PE real concluiu **PASS**. O ajuste de reflow `scripts/multilang/layout_dialogs.py` também foi habilitado somente para os hashes exatos conhecidos da imagem original com glifos e da TEST3.

### Proveniência e privacidade

O corpus textual foi produzido em GitHub Actions por `prepare-trilingual-local-integration.yml` a partir das revisões de código-fonte EN/ES fixadas, sem ROM, XEX, áudio ou PE privado. Depois, os scripts de integração foram executados **localmente** sobre a imagem TEST3 do usuário, não no GitHub público.

- Workpack de corpus real: [Actions run 38335502354](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38335502354) PASS.
- Regressão do catálogo JSON: [Actions run 38335811493](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38335811493) PASS.
- Validação independente: relatório local privado `TRILINGUAL_REAL_TEST3_STATIC_AUDIT_2026_10_12.json`.
- **Backup do PE intermediário e relatórios** (Biblioteca privada, não GitHub): `/Xbox360 - SM64 PTBR/SM64_TEST3_TRILINGUAL_DATA_STAGING_PRIVADO_2026-10-12.zip`, ID `libfile_d1affc8caa3c819193c8e2db0f6bb29e`, SHA-256 `dec42ea2228d0b52e16ec900f1314fe8fbc66da241e9ecde723abdf2c5af6c6c`. ZIP íntegro, 7.414.645 bytes. **Contém PE intermediário, NÃO é XEX e NÃO deve ser executado no Xbox.**

## Bloqueios restantes — sem mascarar como versão final

- O seletor Português / Español / English **não está ligado à tela inicial** nem ativa as tabelas. A rotina PPC da troca existe e passou em emulação, mas ainda precisa ser integrada ao fluxo *seguro* de título.
- Menus de save/interface não cobertos pelas tabelas de 170 diálogos, 26 áreas e 90 estrelas ainda requerem localização/revisão.
- O novo PE não foi convertido para XEX final; não há resultado de boot nem teste de estrela→castelo em build multilíngue.
- A equivalência editorial integral das três traduções (sentido de cada frase, além das ações dos botões) ainda precisa de revisão.
- Não usar o hook de créditos em `0x820CD128` ou o gancho de título anterior em `0x820D5F48`, associados aos testes rejeitados. TEST3 permanece referência que **passou** no Xbox.
- Nenhuma dublagem incluída, conforme prioridade atual do proprietário.

**Próxima tarefa:** ativação segura na intro, validação de menus completos, round-trip XEX e teste em Xbox nos três idiomas (boot, seleção, textos, save, estrela, retorno ao castelo).
