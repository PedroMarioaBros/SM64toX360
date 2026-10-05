# Teste 1 — seletor multilíngue 30 FPS
Data: 05/10/2026. Classe: FIRST_HARDWARE_TEST_CANDIDATE; hardware_verified=false.

## Resultado
Pacote privado: SM64_30FPS_MULTILANG_SELECTOR_TEST1.zip.
XEX: 17.182.720 bytes, SHA-256 075f2ef231c583d7229ecd713f0c330e11ce65434dd1f5d415b73fcc544c1ee6.
ZIP: 17.184.968 bytes, SHA-256 cc603c78bf89439b1bfb3b641c442e08c968bfa309791ddcd890c18613ce7fb3.
Referência persistente para recuperação: libfile_d7b188878d2481919620f4b020550e05.
Não publicar o binário neste repositório público.

## Evidências
- docs/DIALOG_LAYOUT_VALIDATION_2026_10_05.json
- docs/SELECTOR_TEST1_INTEGRATION_2026_10_05.json
- 510 ponteiros, 170 PT-BR byte-idênticos, 170 metadados de linhas conferidos com construtor recuperado.
- Nenhuma alteração fora de .lang em relação ao PE de integração estática anterior.
- Gate e ativação PPC PASS; round-trip PE idêntico.
- 107 diálogos EN e 106 ES excediam limite de largura 125 antes do reflow; nenhum depois.
- Quebras de linha e espaçadores D0 ajustados; palavras e pontuação mantidas. Dez respostas por idioma alinham última linha da página.

## Correção do extrator
0x9E7CD8 aponta ao membro de ponteiro (+12) do primeiro registro.
linesPerBox é ponteiro-8. Leitura anterior em ponteiro+8 pegava registro seguinte.
Metadados corretos conferidos 170/170; ASCII preferido a aliases JP no texto decodificado; pool PT permanece byte-idêntico.

## Hashes históricos
Os pools de hashes 819dba…/361bce… não foram recuperados. Pesquisa por título SM64 não encontrou pacote multilíngue entre arquivos preservados; consulta de runs para f5cebc7 retornou vazia, mas o conector limita esse endpoint a eventos PR, portanto não prova ausência de runs.
Relatórios 0eec9d8 e ad3cb75 já registravam hashes que reproduzem fontes/scripts atuais ou conversor anterior.
A origem dos hashes divergentes continua sem prova. Não é declarada resolvida.
Este novo candidato é validado independentemente; não depende de alegar igualdade com pools históricos desconhecidos.

## Reproduzir (com bytes privados recuperados)
1. Extrair PT da v0.4 canônica; importar fontes EN/ES fixadas e localizar controles.
2. Executar audit_pool_reproducibility.py sobre pools sem layout (relatório baseline).
3. Executar layout_dialogs.py glyphs.pe.
4. Executar build_dialog_pools.py --layout e validate_localization.py --layout.
5. Executar build_lang_section.py --base-pe glyphs.pe --dialogs-dir _localization_build --output-pe layout-lang.pe.
6. Executar integrate_gate.py layout-lang.pe previous-validated.pe layout-gate.pe _localization_build integration.json.
7. Executar test_language_activation.py e test_pregame_gate.py.
8. Executar xex2replace v04.xex layout-gate.pe candidate.xex basic.
9. Extrair com xex2ool basefile candidate.xex -o roundtrip.pe; exigir igualdade byte a byte.
A referência previous-validated.pe tem SHA-256 315498a8ca65cbff54d83b9654b9c6fe7fe2efa4f66ae7aee2dfeecddab04769; glyphs.pe 5b4ec5d2f79ecc1cbe23b5d01b7657e4b7ac619937584ea09e2ec26443e2cdf1.
Falhar se hashes/referências não conferirem; não remover guardas para prosseguir.

## Teste Pedro
Extrair em pasta separada e abrir default.xex.
Verificar créditos → seletor; D-pad cima/baixo; A confirma.
Reiniciar para escolher cada um dos três idiomas e abrir primeiro diálogo.
Verificar glifos ES, caixas de texto, save existente, salvar/sair e reabrir.
Registrar boot/travamento, tela exata, idioma e evidência visual.
Menus/cursos/estrelas podem continuar PT-BR nesta etapa; dublagens novas não estão integradas.

## Próxima etapa
Aguardar/registrar resultado real do seletor no console. Se falhar, corrigir o caso observado; se passar, completar interface PT/ES/EN antes das novas vozes.
