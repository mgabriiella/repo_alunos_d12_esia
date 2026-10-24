# Registro individual — AV2

Estudante: **Maria Gabriella da Silva Calado** — Data: **21/10/2026**  — Caminho: **B (MiniLoja)**

## Escopo (seis campos)
- **Objetivo:** separar subtotal, desconto e frete de `calcular_total` em funções nomeadas e usar `FRETE_POR_UF`/`TAXA_POR_UF` (já declaradas e nunca usadas) como fonte única, sem mudar nenhuma saída.
- **Pode tocar:** só `trabalho/miniloja/calculo.py` (cópia de `caso/`) e as pastas novas `verificacao/` e `docs/`.
- **Não pode tocar:** a assinatura `calcular_total(itens, cupom=None, uf="PE")`, `caso/`, `testes/`, `regras.md`, os demais módulos e a suíte existente.
- **Invariantes:** golden master idêntico (repr e tipo); ordem desconto → frete → taxa; `flags.promo_natal_ativa()` lida só para `NATAL`.
- **Pronto quando:** golden `OK`, suíte existente com 26 `OK`, suíte do contrato verde e mutação sem sobrevivente não justificado.
- **Pare e pergunte se:** algo parecer erro do contrato ou exigir mudar valor cobrado → registrar, sem corrigir.

**Plano do agente e o que cortei.** O plano incluía ou sugeria: (1) migrar para `Decimal`; (2) trocar `> 200` por `>= 200` "porque o contrato diz"; (3) remover o ramo `NATAL` como código morto; (4) simplificar a taxa para `base * (1 + taxa)`; (5) usar dicionário também para cupons. **Cortei os cinco:** (1), (2) e (4) mudam valores cobrados, então não são refatoração; (3) muda o resultado com a flag ligada; (5) não traz ganho. **Acrescentei:** gravar o golden a partir do original antes de qualquer mudança e conferir que `caso/` continua intacto.

## Comportamento preservado
**Método:** golden master com igualdade exata de `repr(float)` e tipo. **Entradas:** 22 carrinhos × 8 cupons (inclui `""`, `promo10` e desconhecido) × 7 UFs (inclui `""` e `pe`) × flag NATAL 0/1, mais 3.000 carrinhos aleatórios (semente 20261021). Cobre as fronteiras de R$ 200 antes e depois do desconto e valores com terceira casa 5.
```
python -B verificacao/gerar_golden.py gravar --codigo caso
  Gravados 5464 casos em golden_calcular_total.json a partir de caso
python -B verificacao/gerar_golden.py comparar --codigo trabalho
  OK: 5464 de 5464 casos idênticos (repr e tipo) em trabalho
python -B testes/test_miniloja.py --codigo trabalho --existentes
  Ran 26 tests in 0.010s  OK
```
**Incidente detectado por mim:** na primeira tentativa o golden deu `OK`, mas `caso/miniloja/calculo.py` já estava com o código refatorado, então eu tinha comparado o novo com ele mesmo. Detectei com `Select-String -Path caso\miniloja\calculo.py -Pattern "_aplicar_desconto"` (apareceram as linhas 40 e 54), restaurei o original com `git checkout -- caso/miniloja/calculo.py`, confirmei que a busca não retornava nada e gravei o golden de novo. As saídas acima são da segunda gravação.

## Testes derivados do contrato (`verificacao/test_contrato_calculo.py`, 23 testes)
Cada esperado foi calculado a partir de `regras.md`, com a conta no comentário do teste.

| Teste (regra) | Como provei que falharia | Resultado |
|---|---|---|
| NATAL com campanha: 50 × 0,80; SP → 64,09 (R1.2) | mutantes NATAL 21%, ignora flag, nunca aplica | 3 mortos |
| RJ: (70 + 21,50) × 1,06 → 96,99 (R1.3/R1.4) | mutantes frete RJ e taxa RJ | mortos |
| Ordem: 220 × 0,9 = 198 → paga frete → 233,15 (R1.6) | mutante "frete olha subtotal sem desconto" | morto |
| 199,99 → 223,53 e 200,01 → 210,01 (R1.3) | mutantes limite 200→300 e `or`→`and` | mortos |
| PE: (33,33 + 12,90) × 1,05 = 48,5415 → 48,54 (R1.5) | mutante "arredonda em 3 casas" | morto |
| D1/D2 com `expectedFailure` (R1.3/R1.5) | mutantes `>=` e `x*(1+t)` viram "unexpected success" | mortos |
```
python -B verificacao/test_contrato_calculo.py --codigo trabalho
  Ran 23 tests in 0.005s  OK (expected failures=2)
python -B verificacao/mutacao_refatorado.py
  25 mutantes; contrato: 24 MORTO, 1 vivo; golden: 24 MORTO, 1 vivo
  Suíte do contrato: 24/25 mortos. Sobreviventes: ['subtotal começa em 0.0']
python -B verificacao/gerar_golden.py comparar --codigo trabalho   (depois da mutação)
  OK: 5464 de 5464 casos idênticos (repr e tipo) em trabalho
```
**Sobrevivente:** `total = 0` → `total = 0.0` é **equivalente**: `0 + x` e `0.0 + x` dão o mesmo float, e o carrinho vazio termina em `round()` de um float nos dois casos. O golden, que compara repr e tipo, também não o distingue. O equivalente da suíte original (`desconto_aplicado`) deixou de existir porque a variável foi removida.

**Divergências contrato × código (não corrigidas, ver ADR-001):** D1, frete grátis com `> 200` em vez de `>= 200` (2 × R$ 100 em PE: contrato 210,00, código 223,55); D2, `round()` em vez de meio para cima (2 × R$ 1,00 em PE: contrato 15,65, código 15,64). A suíte existente grava os dois valores em `test_cenarios_gravados`.

## Documentação
Docstring de `calcular_total` com o contrato R1, D1/D2 e o motivo da forma das operações em float. `docs/ADR-001-calcular-total-divergencias.md` registra contexto, decisão, consequências, alternativas e a condição para rever.

## O que a IA errou (o quê, onde, como detectei)
1. **Padrão ambíguo na mutação:** em `mutacao_refatorado.py`, o trecho `_frete(com_desconto, cupom, uf)` aparecia na chamada e no `def`. O `assert count == 1` do script parou a execução, e o padrão foi trocado por `+ _frete(...)`.
2. **Instalação sem conferência de `caso/`:** o passo a passo não mandava conferir que `caso/` continuava original antes de gravar o golden, e isso gerou o falso `OK` descrito acima. Detectei com `Select-String`.
3. **Arquivos indisponíveis para download:** a IA apresentou o registro e o ADR em `docs/`, um caminho que não existia na área de download, e o download falhou. Ela corrigiu ao apresentar os arquivos avulsos.
4. **Método frágil para criar arquivo:** ao recriar no PowerShell o `mutacao_refatorado.py`, que tinha baixado vazio (0 bytes), a IA sugeriu colar um bloco longo com `@'...'@`. A colagem foi cortada, e depois a linha `@'` foi salva no arquivo (`SyntaxError` na linha 1). Removi as linhas extras e confirmei com `Get-Content -TotalCount 1`.

## Limite da verificação e condição para rever
O golden prova igualdade só no domínio amostrado: `uf` e `cupom` como str/None, preços até 250, até 4 itens. Com `uf` não-hashable o original caía em "demais UFs" e o refatorado lança `TypeError` (fora do contrato). Na suíte do contrato, a morte de `x*(1+t)` depende do teste D2: se D2 for corrigido, só o golden mata esse mutante. R2, R3 e R4 não são cobertos. Os números de sabotagem do golden (269, 177 e 262 divergências) e a comparação com `testes/mutacao_manual.py` (17/18 contra 15/18) foram observados pela IA na preparação; não os repeti. Rever quando D1/D2 forem decididos (ADR-001).

## Procedência/IA
Ferramenta e modelo: Claude Opus 5.5 (Anthropic), via claude.ai. Tarefa delegada: plano, código refatorado, scripts de golden e mutação, testes do contrato, ADR e rascunho deste registro. Trecho aproveitado: os arquivos de código e teste como entregues. Minha verificação/intervenção: rodei no Windows (PowerShell) todos os comandos com saída mostrada neste registro, detectei e corrigi o golden gravado com o código errado, recriei o script de mutação que baixou vazio e revisei as contas dos testes. O raciocínio e a decisão registrados são meus.

**Anexo — resumo do diff:** `caso/miniloja/calculo.py → trabalho/miniloja/calculo.py`: 1 arquivo, +57/−62 linhas. Novos: `verificacao/gerar_golden.py` (81 linhas), `verificacao/golden_calcular_total.json`, `verificacao/test_contrato_calculo.py` (166), `verificacao/mutacao_refatorado.py` (76), `docs/ADR-001-calcular-total-divergencias.md`.
**Revisão:** [x] escopo; [x] comportamento; [x] testes com prova; [x] documentação; [x] erros da IA; [x] limite.
