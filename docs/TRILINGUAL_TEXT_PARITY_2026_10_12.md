# Localização trilíngue — avanço real de 12/10/2026

## Objetivo confirmado pelo proprietário

Uma única edição do SM64 para Xbox 360 com `Português`, `Español` e `English`. O conteúdo do jogo deve ser equivalente nas três versões; a única diferença deve ser o idioma em que a mesma informação é comunicada. Todas as referências aos comandos devem nomear **os controles reais do Xbox 360**, e não os do Nintendo 64. A tradução PT-BR da PMCN Studios aprovada pelo proprietário **não pode ser substituída nem reescrita**. Inglês deve continuar original, com localização dos comandos; espanhol usa fonte traduzida existente e recebe reparos explícitos de divergências. Vozes/dublagem foram **adiadas por decisão do proprietário**.

## Base de execução segura

Teste A/B **no console**, confirmado por Pedro: TEST3 30 FPS permitiu coletar estrela e voltar ao castelo **sem crash**. O pacote posterior de créditos/menu corrigido reintroduziu o Fatal Crash após estrela. Comparação binária documentada em `docs/STAR_RETURN_CRASH_2026_10_12.md`.

**Não inserir de novo a rotina de créditos por hook global em `0x820CD128`.** O seletor precisará ser colocado no fluxo legítimo da introdução/menu de título, mantendo intacta a transição entre fase e castelo. Nenhuma compilação trilíngue foi liberada para console nesta etapa.

## Materiais identificados (fixados nos mesmos commits anteriores)

- EN: `n64decomp/sm64@9921382a68bb0c865e5e45eb594d9c64db59b1af` — textos originais em inglês.
- ES: `Reonu/ultrasm64-spanish@b720e8328c4ead21e3eac5dfceb21edba38ed79b` — tradução completa em espanhol da Espanha, usada como referência; não importá-la como texto final sem auditoria.
- Também identificada a tradução `Blade133bo`, v4.1 de 18/09/2026, que adapta texto do SM64 DS. É útil para consulta, mas a diferença da linha narrativa e a ausência de fonte adaptada no nosso pipeline impedem substituir automaticamente a fonte Reonu. Referência https://romhackplaza.org/translations/super-mario-64-spanish-translation-nintendo-64

## O que de fato ficou processado em scripts

**Diálogos:** 170 EN e 170 ES importados e adaptados semanticamente aos botões Xbox. PT-BR canônico 170 diálogos **não alterado**.

**Controles:** mapeamento N64→Xbox da versão canônica documentado em `localization/manifests/controller_mapping.json`. 34 diálogos de instrução identificados na união das fontes, incluindo o ES ID 149 com referência adicional ao analógico de movimento. O script `scripts/multilang/localize_controller_texts.py` agora processa **todos os 170 diálogos** e falha se uma conversão inesperada ocorrer fora do conjunto auditado; não usa substituição isolada cegamente nem deixa tokens N64 restantes. A verificação independente `scripts/multilang/audit_language_parity.py` exige cobertura de classes de ações (A, X, LT/LB, RB/RT, analógico esquerdo e direito) para cada diálogo que as contém originalmente.

**Divergências espanholas reais corrigidas de forma estrita**, em `scripts/multilang/es_semantic_errata.py` (falha se a frase original mudar):
- 015: restaurar instrução de executar chute com A seguido de X, omitida no roteiro ES de referência;
- 030: corrigir redação em espanhol dos irmãos Lakitu;
- 032: explicitar colocar gorro alado antes do salto triplo e corrigir verbo;
- 034: restaurar instruções para continuar (A), alternar câmeras (RB/RT) e consultar placas, omitidas no ES;
- 046: explicitar o botão A na instrução do salto entre paredes.
O script aplica as correções **somente no ES e antes de ajustar as linhas ao limite de largura**. EN continua com as falas originais salvo controles; PT-BR não é tocado.

**Cursos/estrelas secretas:** `scripts/multilang/import_course_catalog.py` importa e verifica por identificador **15 fases, 90 missões, 10 posições de fases secretas, 1 cabeçalho e 7 textos auxiliares** em EN e ES. Alinhamento de IDs e quantidade PASS. Corrigida grafia `ISLA FLOANTE` → `ISLA FLOTANTE` na missão apropriada da Fortaleza de Whomp. Os catálogos gerados permanecem em `_localization_build`, não são distribuídos como ativos do jogo.

## Validação automatizada efetivamente executada

GitHub Actions [Trilingual Text and Xbox Controls Audit](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/38333296556):

- **8 testes** de erratas e controles: PASS;
- **5 testes** de presença e alinhamento de categorias de controle: PASS;
- **5 testes** de fases/missões: PASS;
- Importação real de `text/us/dialogs.h` e `courses.h` das revisões fixadas;
- Validação real **PASS_INPUT_CLASS_COVERAGE** (170 EN/170 ES, zero classes de botão ausentes, zero tokens N64 residuais, zero referências ambíguas a analógico N64);
- Validação real **PASS_STAGE_ID_ALIGNMENT** (15×6, segredos e textos auxiliares);
- 18 testes sintéticos no total, mais as duas auditorias reais sobre fontes externas. `Multilang Static Check` também passou após a correção do item 149.

**Escopo dos PASS:** cobertura/identificação mecânica dos textos e controles. **Não** é garantia de equivalência semântica completa entre idiomas. A revisão editorial de todos os 170 diálogos, nomes de fase, textos de interface e placas ainda é necessária, especialmente para evitar histórias/instruções omitidas ou divergentes. PT-BR não foi reextraído/rehash nesta nova CI porque o executável é privado; sua versão canônica já tinha SHA-256 de pool `0b913e5c728f3991c8885df8b4b262b9f68de54cce5b485e46fa101765a84c9a`.

## Pendências de implementação, em ordem de segurança

1. Terminar revisão de equivalência EN↔ES↔PT e mapeamento dos textos **fora dos 170 diálogos** (menus de save, títulos/nomes de missões, tela Press Start, placas/dialogs e mensagens finais).
2. Integrar os catálogos de fases e toda UI em estruturas multilíngues do Xbox; os dados de `course_catalog.json` ainda **não são escolhidos em runtime**. As 170 tabelas `.lang` anteriores têm integração apenas estática, não passaram no teste completo de console.
3. Implementar **seletor de idioma na introdução**, sem hook global de execução de level script responsável pela regressão, preservando save, câmera, controles e 30 FPS.
4. Gerar candidato XEX apenas com mudanças rastreáveis, roundtrip PE e comparações de diferenças. Testar boot → escolher idioma → textos/menus → coletar estrela → voltar castelo → save, repetido nos três idiomas. Sem esse teste, **não marcar estável**.
5. Dublagem/vozes ficam em espera; as seis WAVs anteriores continuam preservadas, mas não participam da nova meta.

**Situação real:** textos-fonte EN/ES processados com auditoria de controles e nomes de fases; **nenhum novo XEX trilíngue entregue ou validado**, sem alterar o PT-BR aprovado.
