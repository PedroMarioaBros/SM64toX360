# TEST12 — relatório de patch estático da interface
Data: 20/10/2026

## Resultado da implementação no código

Foi criado `scripts/multilang/test12_live_ui.py`, um patcher fail-closed que exige a PE mapeada exata da TEST11 pelo hash `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`. O patcher altera somente o wrapper do seletor, a rotina auxiliar em cave livre, os metadados/tabelas de `.lang` e os novos dados anexados à cauda livre de `.lang`.

Execução local sobre a PE TEST11 recuperada:
- PE de entrada: 17.170.432 bytes; SHA-256 `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd`.
- PE candidata gerada: SHA-256 `a71a6409b42de7e03db856654ba44540b462d3d71c5b650c6eb01c939ec6226b`.
- Wrapper: 584 bytes, dentro do cave de 768 bytes.
- Auxiliar de tradução do menu de saves: 108 bytes, dentro do cave livre de 256 bytes em `0x823BCB00`.
- 30 rótulos/strings de menu e estado/score preparados para PT-BR, Español e English, com verificação de que cada texto cabe no buffer existente.
- `.lang+0x80–0x87` (scratch B/Y) preservado byte a byte.
- Hook global de `level_script` preservado byte a byte.
- Estado inicial configurado para English (`index=2`).

## Testes automatizados

A workflow [TEST12 Trilingual UI Static and CPU Tests](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39377225771) passou em 20/10/2026: 4 testes estáticos e 5 cenários de CPU PPC. Ela verifica limites de código, buffers, prévia dinâmica com acentos, ordem/direcionais, prompt Start e cópia das strings do menu após A.

## Limitações e status real

- Smoke test específico no Xenia Canary Linux com renderizador nulo: TEST11 e TEST12 ficaram executando por 8 segundos sem mensagens de fatal/exception; o backend nulo registrou falhas de desenho esperadas e **não fornece validação visual**. Xbox físico ainda não testado.
- A prévia do seletor usa o renderizador nativo de glifos, com acentos codificados; a ordem visual é English → Español → Português e os IDs internos são 2=English, 1=Español, 0=Português. A aparência final dos glifos ainda precisa de validação visual.
- XEX candidata empacotada com `xex2replace`: SHA-256 `d4a15796f13e9239aeba02cc446b0a0224ae9579b3af8e5564469454e2427d06`. A extração/decriptação do payload e um segundo roundtrip reproduzem exatamente a PE candidata (`1a5ff2...`).
- Não foi alterado o sistema de dublagem; permanece fora do escopo.


## Resultado físico TEST12 — relato de 20/10/2026

O proprietário testou a XEX TEST12 no Xbox 360. A tela de créditos passa e o seletor chega à face do Mario; a ordem/estado das opções funciona (English, Español, Português), mas **nenhum texto do seletor é renderizado** — só aparece o marcador circular. Após confirmar, o prompt Start muda corretamente para o idioma escolhido; no menu de saves, o título e os demais rótulos parecem traduzidos, porém os quatro slots vazios continuam mostrando `NOVO` em PT-BR mesmo em English/Español.

Diagnóstico novo: o wrapper TEST12 chama `0x82143110` para desenhar os textos do seletor, enquanto o renderizador nativo já identificado e usado pelo código anterior é `PRINT_CENTER=0x8212B498`. Foi corrigida a chamada no código e atualizados os testes de runtime para exercitar o renderizador conhecido. Essa correção ainda precisa passar no CI e ser empacotada/testada; não existe nova XEX validada a partir dela neste momento.

Direção de UX sugerida: o proprietário gostou do seletor sem texto e propôs seta para a direita + bandeira de cada idioma (EUA, Espanha, Brasil). A proposta é boa e mais limpa; contudo, bandeiras exigem um caminho gráfico/sprite que ainda não foi provado no patcher. Próximo passo seguro: validar primeiro a correção do renderizador, investigar o texto `NOVO` nos slots e, em paralelo, auditar um método seguro para desenhar ícones/flags. Não presumir que o suporte a glifos de texto já permite desenhar bandeiras.


## Complemento de diagnóstico — 20/10/2026 (após a revisão TEST13)

### Corrigido com segurança: rótulo dos slots vazios
A string original `NOVO` está no VA `0x829E7170`, em um buffer de exatamente cinco bytes: `17 18 1F 18 FF`. O próximo texto começa imediatamente no byte seguinte; portanto, substituir o conteúdo diretamente por `NUEVO` causaria sobreposição. A correção preparada redireciona o ponteiro no callsite `0x823BC600` para uma função PPC de 96 bytes no espaço livre `0x823BCF48`. Essa função escolhe o ponteiro em `.lang+0xAC/+0xB0/+0xB4` segundo o idioma e preserva r0, r10, r11 e CR. Os textos são `NOVO`, `NUEVO` e `NEW`, nessa ordem interna dos IDs PT-BR, espanhol e inglês.

Os testes automatizados verificam o tamanho da função, o callsite original, os ponteiros, os textos e a preservação dos espaços B/Y e do hook de nível. O workflow **TEST12 Trilingual UI Static and CPU Tests** passou no commit `9058ee7b7386a8099fbc6c76e421109c724751a4`; a verificação estática multilang também passou. Isso valida patcher e instruções PPC em emulação de CPU, não a aparência no Xbox.

### Experimento de renderização revertido
A troca das cinco chamadas do seletor para `PRINT_CENTER=0x8212B498` foi testada e **não será mantida**. Em variantes Xenia com esse caminho, apareceu um crash guest em `PC 0x8215F1A4`, leitura em `0x0000000100000000`; o TEST12 original não apresentou esse dump no mesmo ensaio de 14 s. A execução usava o backend `--gpu=null`, que informou falha ao inicializar Vulkan e erros de backend gráfico, então o ensaio não prova comportamento em hardware físico. Mesmo assim, há regressão correlacionada suficiente para bloquear essa troca. O código voltou ao caminho de chamada de TEST12 (`0x82143110`), que mantém o seletor sem os rótulos visíveis observados pelo proprietário. Não tratar a correção do texto do seletor como concluída.

### Estado da build local exploratória
Foi empacotada uma variante local de investigação com apenas a correção do rótulo dos slots, sem trocar o renderizador do seletor. A extração criptográfica de retorno reproduziu exatamente a PE mapeada, SHA-256 `60ca28a136aa33ae3c93182786493949a1b9fa40766c77b218de3a27abc8e8ae`; a XEX de teste tem SHA-256 `bf6f51fd27cb302ef477f59244b04d634a029116d0c379cc3080b13f81eab16b`. No Xenia Canary Linux com backend nulo, ela rodou 14 s sem dump de crash, mas o backend gráfico estava indisponível; isso não é validação visual nem motivo para considerá-la versão final. Ela não foi enviada ao proprietário como build final.

### Próximo passo seguro
Manter as correções de ponteiro para `NOVO/NUEVO/NEW`; não trocar o caminho de desenho de rótulos por `PRINT_CENTER` sem isolar o crash. Continuar investigando o pipeline gráfico para a seletora sem texto — seta e bandeiras EUA/Espanha/Brasil — usando os pontos de entrada de frame/render já documentados, com limites claros de alteração e testes antes de empacotar uma nova XEX. A baseline é 30 FPS; dublagem e Native60 continuam fora desta fase.
