# TEST9 Fatal Crash → TEST10 com leitura isolada dos controles — 17/10/2026

## Ponto de partida: fatos reais de hardware

- **TEST3**: último XEX aprovado para pegar estrela e retornar ao castelo.
- **TEST8**: exibiu `IDIOMAS TESTE8`, `PORTUGUES`, `ESPANOL` e `ENGLISH` na TV do Xbox, conforme fotos; **PASS visual**, não interativo.
- **TEST9**: abriu, mostrou créditos iniciais, deu **FATAL CRASH ao entrar na tela do seletor**. Reprovada; não pedir reteste. Oito testes PPC32 sintéticos PASS não se traduzem em aprovação Xbox.
- A dublagem está formalmente **fora do escopo** até os três idiomas, seletor e gameplay funcionarem em hardware e o proprietário autorizá-la novamente.

## Isolamento da próxima mudança

A comparação de imagens mapeadas TEST8→TEST9 demonstrou que a TEST9 acrescentou várias operações simultâneas: leitura da estrutura de controle por `gPlayer1Controller`, escrita em `buttonPressed` para bloquear Start, lógica D-pad/A, seleção por estado e cópia de 170+26+90 ponteiros. O ponto causal do Fatal Crash ainda **não foi identificado**.

Foi criada a **TEST10, estritamente diagnóstica de LEITURA**, tomando como base o PE exato da TEST8 aprovada visualmente. Ela preserva o desenho do título pelo renderizador nativo, lê `buttonDown` do controller atual e desenha um `X` ao lado de um dos três rótulos **somente enquanto** o botão correspondente estiver pressionado:

- D-pad UP (`0x0800`) → X na linha PORTUGUES (não seleciona português);
- D-pad DOWN (`0x0400`) → X na linha ESPANOL;
- Xbox A (`0x8000`) → X na linha ENGLISH;
- Sem botão ou ponteiro controlador nulo → sem X.

Não há escrita na estrutura global dos botões, não há ativação de idioma, não há bloqueio de Start, não há novo estado persistido, não há alteração das tabelas PT/ES/EN nem do ciclo estrela→castelo. Este teste deve distinguir **acesso ao controle** do restante do novo código da TEST9; não é uma correção completa.

### Região exata no executável

- Base PE TEST8: SHA-256 `fab6a7c31d1fa2cb4aea3ad5e0f3171bde5248a13f48bbcab56d2bc05fc4c438`;
- Nova rotina PPC `0x823BCD00`: **204 bytes**, SHA-256 `4fd27ff93e2ed0140a849e971b0a9bcdcd39f0b86665506f0af8c78a956b4a6f`;
- A chamada `intro_regular→wrapper` em `0x821472D4` permanece a mesma já testada visualmente pela TEST8;
- Ponteiro de controle: lido em endereço global `0x823C8990` (imediato PPC assinado, high `0x823D`, low `0x8990`), depois `lhz` **somente leitura** em `controller+0x10` (buttonDown);
- Novos textos curtos `TESTE10` e `X` anexados à região ainda livre da seção `.lang`, sem mover os pools ou ponteiros existentes;
- Diferenças TEST8→TEST10: **94 bytes efetivamente distintos**, todos confinados ao wrapper, cursor de `.lang` e novos rótulos; região de código do jogo fora do wrapper permanece idêntica à TEST8;
- Hooks perigosos da execução global de level script não reinstalados; B/Y originais preservados.

### Validação técnica efetivamente realizada

- [GitHub Actions 39012707192](https://github.com/PedroMarioaBros/SM64toX360/actions/runs/39012707192): **5 testes PPC32 PASS** — sem botão, UP/DOWN/A com posicionamento do X, controle desconectado, Start não alterado, preservação do campo buttonPressed, stack e registradores.
- Esses testes são **CPU32 sintéticos**; não equivalem a execução completa no Xbox PowerPC64. O probe PPC64 anterior com Unicorn 2.1.4 deu `UC_ERR_EXCEPTION` **antes da primeira instrução** e foi classificado corretamente como INCONCLUSIVO, não como a causa do crash.
- Reconstrução XEX2 Basic a partir do XEX TEST8 original com utilitário host já usado nas versões anteriores;
- **Round-trip completo XEX→PE AES: byte-idêntico PASS** à imagem TEST10 preparada;
- ZIP CRC PASS, conteúdo conferido.

### Binários de diagnóstico e recuperação

- ZIP: `SM64_TEST10_DIAGNOSTICO_LEITURA_CONTROLES_30FPS.zip`, **17.189.927 bytes**, SHA-256 `51e6ca289a2e58d30d9e3cc7bf0648ab7f96798332f040d97c0757771bc10347`;
- `default.xex` SHA-256 `ffa460aab10a0877f084289d7cf1e3b3aa44078d3afc8d7b0919a81ba1a2cfab`, 17.182.720 bytes;
- PE mapeado SHA-256 `15423bd657f438e0e90f1744a8af5b5aad8f07b72eb5eaadf96655f99b0b604c`, 17.170.432 bytes;
- Source auditável: `scripts/multilang/test10_controller_read_probe.py`;
- Testes PPC isolados: `scripts/multilang/test_test10_readonly.py`;
- CI: `.github/workflows/test10-controller-readonly.yml`;
- ZIP privado preservado na Library: `/Xbox360 - SM64 PTBR/SM64_TEST10_DIAGNOSTICO_LEITURA_CONTROLES_30FPS.zip`, library id `libfile_93000491b92c8191b2e4f2f882c5bbe3`;
- O ZIP contém XEX, instruções, relatório e dois scripts de auditoria. Não publicar executáveis/PE no GitHub público.

## O que testar no Xbox agora

Em **pasta separada**, preservando a TEST3 funcional, TEST8 visual e saves:

1. Abrir TEST10 e observar a tela inicial: deve aparecer `TESTE10` mais três idiomas com letra colorida;
2. Segurar **UP** no D-pad: X temporário na linha PORTUGUES;
3. Segurar **DOWN** no D-pad: X temporário na linha ESPANOL;
4. Segurar **A**: X temporário na linha ENGLISH;
5. Soltar: X deve desaparecer. Não usar Start, saves ou fases.

- **Se Fatal Crash** na abertura: parar, informar se chegou a aparecer `TESTE10`. Isso isola leitura de controle/ramificações/render adicional como suspeitas, não prova automaticamente um culpado único.
- **Se aparece a lista, mas nunca o X**: não alterar mais código às cegas; investigar flags, ponteiro, mapeamento e frame ativo.
- **Se X responde**: o caminho de leitura e indicador está funcional em hardware; próxima etapa será seleção com estado **sem escrever em buttonPressed**, depois ativação segura das tabelas PT/ES/EN.

**Status:** TEST10 XEX compilado e auditado; resultado Xbox **PENDENTE**. Seletor PT/ES/EN ainda não funcional. Dublagem continua PROIBIDA nesta etapa.
