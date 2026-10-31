# Escopo e plano — AV3, caminho B1 (R4: acesso a pedidos)

Escrito antes de qualquer mudança no código.

## Escopo (seis campos)
- **Objetivo:** `get_pedido` só devolve o pedido ao próprio dono (R4: um usuário só pode ver os próprios pedidos).
- **Pode tocar:** `caso/miniloja/handlers.py` (função `get_pedido`) e `caso/testes_existentes/test_handlers.py` (só acrescentar teste).
- **Não pode tocar:** `caso/regras.md`, `testes/`, demais módulos de `caso/miniloja/`, asserções de testes existentes, assinatura de `get_pedido`.
- **Invariantes:** o dono recebe `200` com o pedido; pedido inexistente continua `404`; as outras rotas não mudam; os 26 testes existentes continuam verdes.
- **Critério de pronto:** o teste negativo falha antes da correção e passa depois; suíte existente verde; `git diff --stat` mostra só os dois arquivos acima.
- **Critério de parada:** se for preciso mexer em outro arquivo ou alterar um teste existente, parar e reportar.

## Decisão de design
Pedido de outro usuário responde `404` (igual a inexistente), não `403`: o `403` confirmaria que o pedido existe e permitiria enumerar ids. R4 não define o status; decisão humana.

## Plano
1. Commit do escopo (este arquivo).
2. Teste negativo: usuário B pede o pedido de A → deve receber `404` sem dados do pedido. Rodar e ver falhar.
3. Correção em `get_pedido`. Rodar o teste novo e a suíte.
4. Sabotagem: desfazer a correção e confirmar que o teste volta a falhar.

## Modo de interação
Claude Code em modo plano para propor, depois edição com aprovação manual de cada mudança (sem modo auto).