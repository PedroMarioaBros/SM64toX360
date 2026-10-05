# Instruções permanentes de continuidade
Aplicam-se a todo o projeto SM64toX360.
Por determinação explícita do proprietário, nenhuma sessão deve depender de checkpoint manual fornecido por ele.

1. Antes de trabalhar, ler PONTO_DE_RETOMADA.md e CHECKPOINT_PROJETO.md na raiz.
2. Branch ativa: feature/multilang-dub-30fps. main contém entrada de descoberta; código e evidências atuais ficam na branch ativa.
3. Continuar da próxima tarefa registrada. Não repetir levantamento completo sem mudança relevante ou evidência faltante.
4. Atualizar CHECKPOINT_PROJETO.md após resultados relevantes e antes de cada encerramento, incluindo falhas e bloqueios; acrescentar histórico datado.
5. Publicar e verificar a atualização no GitHub. Não dizer que foi salvo se só existir localmente.
6. Ao trocar de branch, atualizar a entrada na main. Manter checkpoints de main/branch ativa sincronizados quando possível; se não, apontar explicitamente para o mais recente.
7. Progresso exige arquivo/hash/relatório/teste ou feedback real. Separar plano, análise estática, emulação e teste no console.
8. Base atual 30 FPS. Não misturar Native60; preservar PT-BR do usuário byte a byte.
9. Dar atualizações breves durante trabalho; avisar imediatamente erros/bloqueios. Não deixar o usuário aguardando em silêncio.
10. Nenhum encerramento pode declarar entrega final enquanto houver bloqueios de validação registrados.
11. Binários de jogo não são publicados neste repositório público. Registrar hashes e localização recuperável sem expor credenciais.
12. Se ferramentas/acesso não permitirem ler ou escrever, explicar a limitação exata; não inventar continuidade, commit ou resultado.
