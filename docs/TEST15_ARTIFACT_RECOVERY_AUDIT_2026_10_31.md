# TEST15 — auditoria de recuperação de artefatos

Data: 31/10/2026  
Objetivo: recuperar os bytes exatos da PE/XEX TEST15 sem solicitar reenvio ao proprietário.

## Identidades esperadas

- PE TEST14 (entrada do patcher): 17.170.432 bytes; SHA-256 `6266c97deec43d4f43fe3c89bce2ebfb019ab220409702a35fccbd17b0878742`.
- PE TEST15: 17.170.432 bytes; SHA-256 `d1657528056df5f8c1257f3197a2674f69a46ff14dd090b682bea47f4be4a8b4`.
- XEX TEST15: SHA-256 `fcf76cbe7a5e8247341dd4215254eb8a759f989ab42700ccd305eaca09680cc1`.
- ZIP TEST15: SHA-256 `89a2f45e778afcb031d642f2f5820246a67b2584dfbc95874f4883f69454f121`.

## Fontes verificadas nesta retomada

1. **Árvore Git da branch `feature/multilang-dub-30fps`:** não contém arquivos `.xex`, `.zip`, `.bin`, `.exe` ou PE. Contém patcher, testes e relatórios.
2. **GitHub Releases:** endpoint de releases retornou lista vazia.
3. **GitHub Actions TEST15:** execução `39437813460` foi consultada diretamente; `actions/runs/39437813460/artifacts` retornou `total_count: 0`. A execução era teste sintético; não publicou binário.
4. **Outras execuções CI verificadas:** `39438223602` e `39438169429` também não possuem artifacts. O workflow TEST15 executa fixtures sintéticas e não recebe o PE/XEX proprietário.
5. **Library do ChatGPT disponível nesta sessão:** listagem recursiva não encontrou arquivo SM64 TEST14/TEST15, nem pacote com os nomes registrados. Existe um `default.xex` de 692.224 bytes, SHA-256 `80d2bbd304fe48618b27c9d4ca38f7df8d06f04f1e6761bf9f4123e8524e37ba`; tamanho e hash não correspondem à XEX TEST14 de 17.182.720 bytes, portanto foi descartado como fonte e não será usado.
6. **Pasta de trabalho atual:** não contém os pacotes TEST14/TEST15; apenas ferramentas genéricas XEX2 e Xenia.

## Conclusão verificável

Os relatórios e hashes sobreviveram no Git, mas os bytes do binário não. Não foi possível recuperar a PE TEST14/TEST15 exata de nenhuma fonte acessível nesta sessão. Os hashes permitem verificar uma recuperação futura, mas não reconstruir os bytes.

O patcher `scripts/multilang/patch_test15_prompt_demo_fix.py` exige a PE TEST14 exata e falha deliberadamente com qualquer outra entrada. Portanto, não é seguro executar patch de pausa, glifos ou analógico sem recuperar a base correspondente. Não utilizar o `default.xex` de 692.224 bytes: é outro binário.

## Próxima ação técnica

A recuperação precisa vir de um artefato binário preservado fora da árvore Git consultada (por exemplo, pacote de teste guardado no dispositivo/backup do projeto) ou de uma fonte original autorizada com hash verificável. Quando disponível:

1. extrair a PE mapeada da XEX;
2. exigir SHA-256 TEST14 `6266c97...` ou TEST15 `d165752...` conforme a entrada;
3. reconstruir TEST15 da TEST14 e exigir o hash PE TEST15 exato;
4. reempacotar e comparar XEX/ZIP com os hashes registrados, caso a ferramenta e os metadados produzam resultado determinístico;
5. só então iniciar cross-reference dos glifos G/U, textos de pausa e estado analógico.

## Integridade e segurança

- Nenhum binário estranho foi usado.
- Nenhuma PE/XEX nova foi gerada.
- Nenhuma mudança funcional foi aplicada.
- TEST15 permanece a referência física aprovada pelo proprietário.
- Base 30 FPS preservada; Native60 e dublagem fora do escopo.
