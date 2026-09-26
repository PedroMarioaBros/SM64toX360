# Toolchain aberta Xbox 360 — OpenXeChain

## Marco confirmado em 25/09/2026

O repositório auxiliar `PedroMarioaBros/OpenXeChain-X360-Builder` concluiu com
sucesso o GitHub Actions **run #20** (run ID `36198042207`).

O run comprovou:

- build completo do OpenXeChain;
- Clang/LLVM presente;
- xecorelib presente;
- Newlib presente;
- compiler-rt presente;
- SynthXEX 0.0.6 presente;
- compilação de um fonte C para `ppc32-xbox360`;
- link PE com subsystem Xbox 360;
- conversão PE -> XEX;
- geração real de `hello.xex`;
- primeiros quatro bytes de `hello.xex`: `XEX2`;
- empacotamento da toolchain reutilizável.

## Verificação independente do artefato

O artifact `openxechain-x360-toolchain-20` foi baixado e inspecionado novamente
fora do job.

`hello.xex`:

- tamanho: 20.480 bytes
- primeiros 16 bytes:
  `58 45 58 32 00 00 00 01 00 00 10 00 00 00 00 00`
- magic ASCII: `XEX2`
- SHA-256:
  `b5a74eb8781411d03ec7ee16d4c54736a68b890f0dd0bf4545121d097faaf7a5`

Toolchain `.tar.xz`:

- SHA-256:
  `c71a1a4586a2eb1741c632b164ad74e90532cdb7bf0851774544998b35312d37`

Artifact ZIP do Actions:

- SHA-256:
  `5bcf6ac0b741f412adebe31dce98b5673af643a99413658021d1b53e5fbd425e`

## Componentes confirmados dentro da toolchain

- `xenon/bin/clang`
- `xenon/bin/lld-link`
- `xenon/bin/synthxex`
- `xenon/bin/llvm-dlltool`
- `xenon/lib/xecorelib.a`
- `xenon/ppc-xbox360/lib/libc.a`
- `xenon/lib/generic/libclang_rt.builtins-powerpc.a`

## Limite da prova

Esse marco comprova uma cadeia **aberta e reproduzível capaz de gerar um arquivo
XEX2**. Ele ainda não prova que o `hello.xex` inicia em um Xbox 360 real.

O run #20 usou o smoke mínimo:

- `clang --target=ppc32-xbox360`
- `lld-link /entry:main /subsystem:xbox360`
- `synthxex -i ... -o ...`

O run #21 foi criado depois para alinhar o smoke à receita completa do driver
CrossXbox360 do próprio OpenXeChain (`/FIXED`, base `0x82000000`,
alinhamento `0x10000`, entry `_start`). A validação desse segundo smoke é
uma confirmação adicional, não uma condição para reconhecer o sucesso do run #20.

## Consequência para o SM64toX360

A principal barreira de infraestrutura mudou de estado:

**antes:** não havia uma toolchain livre comprovadamente capaz de completar a
cadeia até XEX no nosso ambiente.

**agora:** existe uma toolchain OpenXeChain construída e verificada até um XEX2
mínimo.

Isso ainda não significa que o SM64 possa ser recompilado imediatamente. O
próximo problema técnico é reproduzir/recuperar o backend Xbox 360, fontes e
dependências necessárias do port específico, ou continuar a evolução controlada
por patch binário da base recuperada.
