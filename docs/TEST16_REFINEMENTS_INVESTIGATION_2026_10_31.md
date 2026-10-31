# TEST16 — investigação dos refinamentos após validação física da TEST15

Data: 31/10/2026  
Base funcional: TEST15, 30 FPS  
Estado: **investigação iniciada; nenhum PE/XEX novo gerado**

## Retorno físico do proprietário — TEST15

O proprietário testou as três opções no Xbox 360 real e confirmou:

- English: prompt da attract/demo acompanha o idioma selecionado — PASS.
- Español: prompt da attract/demo acompanha o idioma selecionado — PASS.
- Português: prompt da attract/demo acompanha o idioma selecionado — PASS.
- Seletor abre e funciona; jogo inicia e permanece estável, sem tela preta ou travamento — PASS.
- Letras G e U continuam cinzas — FAIL conhecido.
- Menu de pausa exibe PAUSA em todos os idiomas — FAIL.
- Navegação do seletor ainda depende do direcional; requisito novo: analógico esquerdo deve navegar.

A confirmação física encerra a pendência do prompt da attract/demo: a solução TEST15 deve ser preservada sem alterações desnecessárias.

## Especificação funcional dos três refinamentos

### 1. Glifos G e U

- Corrigir a aparência das letras G e U na tela do seletor.
- A tentativa de usar ASCII maiúsculo já foi testada fisicamente e falhou; não repetir essa hipótese.
- O código existente usa texto ASCII/NUL com o renderer centralizado nativo. Isso não identifica, por si só, a causa do tom cinza.
- Antes de patch, rastrear o caminho real de lookup/renderização e comparar os índices/atributos de G e U com caracteres vizinhos que aparecem corretamente.
- Não alterar a centralização X=160 nem trocar renderer sem prova de ABI e compatibilidade.

### 2. Menu de pausa

Texto solicitado:
- English: PAUSE
- Español: PAUSA
- Português: PAUSE (grafia explicitamente solicitada pelo proprietário)

A ativação atual do idioma troca os 170 ponteiros de diálogo; ela não equivale a uma tradução global de toda a interface. A tabela MENU_ITEMS existente em `scripts/multilang/test12_live_ui.py` cobre itens do menu de saves, não comprova cobertura do menu de pausa. O mapa TEST11 de textos de saves também não mapeia o menu de pausa.

Próximo passo obrigatório: localizar no PE mapeado exato da TEST15 as strings/IDs de pausa, referências cruzadas e rotina de renderização. Determinar se o texto é string fixa, token de charmap ou texto montado por código. Mapear também as demais opções do menu de pausa antes de decidir se só o título ou todo o menu deve ser localizado. Preservar buffers adjacentes e terminadores.

### 3. Navegação pelo analógico esquerdo

- Preferência do proprietário: navegar no seletor pelo analógico esquerdo.
- Manter o direcional como alternativa de acessibilidade/regressão, salvo se a implementação revelar conflito.
- O wrapper conhecido lê atualmente os bits digitais D-pad UP/DOWN (0x0800/0x0400) e A; não há leitura analógica nesse trecho.
- Não inferir offsets de eixo a partir da estrutura XInput bruta. Primeiro rastrear o layout do controlador efetivamente entregue ao wrapper, incluindo escala, sinal, deadzone e momento de atualização.
- Implementar limiar/deadzone e repetição controlada (edge/hold delay) para evitar percorrer as opções continuamente com pequena inclinação.
- Confirmar que a leitura não altera os controles normais do Mario nem a câmera. Analógico direito permanece câmera; o requisito é para o esquerdo apenas enquanto o seletor está ativo.

## Ordem de trabalho

1. Recuperar/confirmar os bytes da PE mapeada TEST15 e sua identidade pelo SHA-256 registrado no relatório TEST15.
2. Mapear G/U no renderer/fonte e produzir diagnóstico reproduzível antes de qualquer alteração.
3. Mapear o menu de pausa e todos os textos/opções relevantes; criar tabela PT/ES/EN com os valores aprovados.
4. Rastrear o formato real do estado do controle e prototipar navegação analógica em harness PPC/CPU, mantendo D-pad e A.
5. Implementar mudanças em patches isolados, cada um com testes fail-closed e auditoria de bytes alterados.
6. Executar CI e auditorias; somente então gerar um único pacote candidato para teste físico.

## Guardrails

- Preservar TEST15 como rollback e referência aprovada em hardware.
- Preservar o seletor centralizado X=160, o bloqueio da demo antes de confirmar, NEW/NUEVO/NOVO e o prompt da attract/demo nos três idiomas.
- Preservar PT-BR e a base 30 FPS.
- Não misturar Native60 nem dublagem.
- Binários PE/XEX do jogo permanecem fora do repositório público.
- **Nenhuma versão será gerada até que os três refinamentos estejam implementados e passem pelas verificações técnicas.**
- Testes sintéticos/CI não serão descritos como validação no Xbox; somente o proprietário pode confirmar o comportamento físico.

## Limitação de recursos nesta retomada

O repositório contém os patchers e relatórios de TEST15, mas não armazena o PE/XEX proprietário (regra permanente do projeto). A PE mapeada TEST15 precisa ser recuperada do pacote privado/artefato local para fazer cross-reference binário e produzir patches exatos. Os hashes registrados permitem verificar a identidade, mas não substituem os bytes. Até a recuperação, qualquer endereço/patch para G/U, pausa ou eixo analógico seria especulativo e não será aplicado.
