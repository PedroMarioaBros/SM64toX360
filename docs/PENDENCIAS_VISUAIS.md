# Super Mario 64 PT-BR — pendências visuais dos menus

Registro da análise de 15/09/2026. Referência: versão 0.4 para Xbox 360. Nenhuma correção foi aplicada nessa análise.

## Problemas confirmados

| Atual | Proposta | Diagnóstico |
|---|---|---|
| PTS. | PONTOS | substituir abreviação |
| COP. | COPIAR | substituir abreviação |
| APAGA | APAGAR | completar infinitivo |
| ESTEREO | ESTÉREO | acentuação |
| VER JOGO | VER PONTOS | clareza |
| DUPLICAR | COPIAR | padronização |

Há também desalinhamentos entre textos e botões; o posicionamento deve ser recalculado pela largura da palavra final na fonte real. As letras J e V da fonte colorida destoam das demais e precisam de revisão visual.

Outras pendências: NAO→NÃO; HA DADOS SALVOS→HÁ DADOS SALVOS; COPIA CONCLUIDA→CÓPIA CONCLUÍDA; PARABENS→PARABÉNS; MEUS PTS→MEUS PONTOS; revisar CERTO como pergunta.

## Offsets na imagem mapeada (base 0x82000000)

PTS. 0x3CD0D0; COP. 0x3CD0D8; APAGA 0x3CD0E0; ESTEREO 0x3CD080; VER JOGO 0x3CD0E8; DUPLICAR 0x3CD068 e 0x3CD10C; COPIA CONCLUIDA 0x3CD144; HA DADOS SALVOS 0x3CD158; NAO 0x3CD180.

As palavras PONTOS, COPIAR, APAGAR e ESTÉREO cabem nas regiões examinadas, mas os usos e posicionamento ainda precisam ser conferidos na implementação.

Integridade da 0.4: XEX `376a1aca746419e29ae64f34802293ba8e97535ae95cee98184e600fea1c3e83`; ZIP `d31bdd7d8396bbeeea2805dd9cdb3f7bfbfee106bf1fc2380b19bc76e33e2b78`.