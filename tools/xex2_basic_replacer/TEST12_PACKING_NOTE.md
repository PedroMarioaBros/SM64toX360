# TEST12 — empacotamento local de XEX

O patcher `scripts/multilang/test12_live_ui.py` produz uma PE mapeada, não uma XEX. Para empacotar uma candidata, usar o artefato host `sm64-xex2replace-linux-host` produzido pela workflow `.github/workflows/build-sm64-xex2replace.yml` e executar:

```sh
./xex2replace default_TEST11.xex TEST12_mapped_PE.bin TEST12.xex basic
```

Antes do uso, conferir que a entrada é o XEX TEST11 cuja PE mapeada tem SHA-256 `a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd` e que a PE de substituição foi produzida pelo patcher fail-closed TEST12. Depois do empacotamento, extrair a XEX novamente e comparar byte a byte a PE extraída com a candidata. Não publicar nem versionar binários do jogo no repositório.

A reconstrução da XEX não substitui o teste Xenia/hardware. Não entregar uma build física antes de concluir o roundtrip e smoke test.
