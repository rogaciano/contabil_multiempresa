# Exemplos Práticos do Sistema Contábil

Este documento apresenta exemplos práticos e casos de uso do Sistema de Contabilidade Educacional, com o objetivo de auxiliar estudantes e professores na aplicação dos conceitos contábeis utilizando o sistema.

## Caso 1: Abertura de uma Empresa Comercial

### Cenário
Abertura da empresa "Comércio Modelo Ltda." com capital social de R$ 50.000,00, sendo R$ 30.000,00 em dinheiro e R$ 20.000,00 em equipamentos.

### Lançamentos Contábeis

1. **Integralização do Capital em Dinheiro**
   ```
   Débito: 1.1.1.01 - Caixa (Ativo Circulante) - R$ 30.000,00
   Crédito: 3.1.1.01 - Capital Social (Patrimônio Líquido) - R$ 30.000,00
   Histórico: Integralização de capital social em dinheiro
   ```

2. **Integralização do Capital em Equipamentos**
   ```
   Débito: 1.2.3.03 - Equipamentos (Ativo Não Circulante) - R$ 20.000,00
   Crédito: 3.1.1.01 - Capital Social (Patrimônio Líquido) - R$ 20.000,00
   Histórico: Integralização de capital social em equipamentos
   ```

### Resultado no Balanço Patrimonial
```
ATIVO                          | PASSIVO
------------------------------|-------------------------------
ATIVO CIRCULANTE      30.000  | PASSIVO CIRCULANTE        0
  Caixa               30.000  |
                              | PASSIVO NÃO CIRCULANTE    0
ATIVO NÃO CIRCULANTE  20.000  |
  Equipamentos        20.000  | PATRIMÔNIO LÍQUIDO   50.000
                              |   Capital Social     50.000
------------------------------|-------------------------------
TOTAL                 50.000  | TOTAL                50.000
```

## Caso 2: Operações Comerciais Básicas

### Cenário
A empresa "Comércio Modelo Ltda." realiza as seguintes operações no mês de janeiro:
1. Compra de mercadorias a prazo: R$ 15.000,00
2. Venda de mercadorias à vista: R$ 10.000,00 (custo: R$ 6.000,00)
3. Pagamento de despesas administrativas: R$ 2.000,00
4. Pagamento parcial a fornecedores: R$ 5.000,00

### Lançamentos Contábeis

1. **Compra de Mercadorias a Prazo**
   ```
   Débito: 1.1.3.01 - Estoque de Mercadorias (Ativo Circulante) - R$ 15.000,00
   Crédito: 2.1.1.01 - Fornecedores (Passivo Circulante) - R$ 15.000,00
   Histórico: Compra de mercadorias a prazo conforme NF 12345
   ```

2. **Venda de Mercadorias à Vista**
   ```
   # Registro da receita
   Débito: 1.1.1.01 - Caixa (Ativo Circulante) - R$ 10.000,00
   Crédito: 4.1.1.01 - Receita de Vendas (Receita) - R$ 10.000,00
   Histórico: Venda de mercadorias à vista conforme NF 001
   
   # Registro do custo
   Débito: 5.1.1.01 - Custo das Mercadorias Vendidas (Despesa) - R$ 6.000,00
   Crédito: 1.1.3.01 - Estoque de Mercadorias (Ativo Circulante) - R$ 6.000,00
   Histórico: Custo das mercadorias vendidas conforme NF 001
   ```

3. **Pagamento de Despesas Administrativas**
   ```
   Débito: 5.1.2.01 - Despesas Administrativas (Despesa) - R$ 2.000,00
   Crédito: 1.1.1.01 - Caixa (Ativo Circulante) - R$ 2.000,00
   Histórico: Pagamento de despesas administrativas do mês
   ```

4. **Pagamento Parcial a Fornecedores**
   ```
   Débito: 2.1.1.01 - Fornecedores (Passivo Circulante) - R$ 5.000,00
   Crédito: 1.1.1.01 - Caixa (Ativo Circulante) - R$ 5.000,00
   Histórico: Pagamento parcial a fornecedores
   ```

### Balancete de Verificação após as Operações
```
CONTA                                  | DÉBITO    | CRÉDITO   | SALDO D/C
--------------------------------------|-----------|-----------|----------
1.1.1.01 - Caixa                      | 40.000,00 |  7.000,00 | 33.000,00 D
1.1.3.01 - Estoque de Mercadorias     | 15.000,00 |  6.000,00 |  9.000,00 D
1.2.3.03 - Equipamentos               | 20.000,00 |       0,00 | 20.000,00 D
2.1.1.01 - Fornecedores               |  5.000,00 | 15.000,00 | 10.000,00 C
3.1.1.01 - Capital Social             |       0,00 | 50.000,00 | 50.000,00 C
4.1.1.01 - Receita de Vendas          |       0,00 | 10.000,00 | 10.000,00 C
5.1.1.01 - Custo das Mercadorias      |  6.000,00 |       0,00 |  6.000,00 D
5.1.2.01 - Despesas Administrativas   |  2.000,00 |       0,00 |  2.000,00 D
--------------------------------------|-----------|-----------|----------
TOTAL                                 | 88.000,00 | 88.000,00 |
```

### Demonstração do Resultado (DRE) do Período
```
DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO - JANEIRO/2025
--------------------------------------------------
RECEITA BRUTA                                 10.000,00
  Vendas de Mercadorias                       10.000,00
--------------------------------------------------
(=) RECEITA LÍQUIDA                           10.000,00
--------------------------------------------------
(-) CUSTO DAS MERCADORIAS VENDIDAS             6.000,00
--------------------------------------------------
(=) LUCRO BRUTO                                4.000,00
--------------------------------------------------
(-) DESPESAS OPERACIONAIS                      2.000,00
  Despesas Administrativas                     2.000,00
--------------------------------------------------
(=) LUCRO LÍQUIDO DO EXERCÍCIO                 2.000,00
```

## Caso 3: Fechamento de Ano Fiscal

### Cenário
Ao final do ano fiscal, a empresa "Comércio Modelo Ltda." precisa realizar o fechamento contábil, apurando o resultado e transferindo os saldos das contas de resultado para a conta de Lucros ou Prejuízos Acumulados.

### Processo no Sistema

1. **Verificação do Balancete Final**
   - Acessar o menu "Relatórios" > "Balancete"
   - Selecionar o período completo do ano fiscal
   - Verificar se todos os lançamentos foram registrados corretamente

2. **Apuração do Resultado**
   - O sistema automaticamente calcula o resultado do período
   - As contas de receitas e despesas são zeradas
   - O saldo resultante é transferido para Lucros/Prejuízos Acumulados

3. **Fechamento do Ano Fiscal**
   - Acessar o menu "Anos Fiscais"
   - Selecionar o ano fiscal atual
   - Clicar em "Fechar Ano Fiscal"
   - Confirmar a operação

4. **Abertura do Novo Ano Fiscal**
   - Acessar o menu "Anos Fiscais"
   - Clicar em "Novo Ano Fiscal"
   - Definir as datas de início e fim
   - O sistema automaticamente transfere os saldos patrimoniais para o novo ano

### Lançamentos Automáticos de Fechamento

1. **Encerramento das Contas de Resultado**
   ```
   # Encerramento das Receitas
   Débito: 4.1.1.01 - Receita de Vendas - R$ 10.000,00
   Crédito: 3.3.1.01 - Apuração do Resultado do Exercício - R$ 10.000,00
   
   # Encerramento das Despesas
   Débito: 3.3.1.01 - Apuração do Resultado do Exercício - R$ 8.000,00
   Crédito: 5.1.1.01 - Custo das Mercadorias Vendidas - R$ 6.000,00
   Crédito: 5.1.2.01 - Despesas Administrativas - R$ 2.000,00
   
   # Transferência do Resultado para Lucros Acumulados
   Débito: 3.3.1.01 - Apuração do Resultado do Exercício - R$ 2.000,00
   Crédito: 3.3.2.01 - Lucros ou Prejuízos Acumulados - R$ 2.000,00
   ```

### Balanço Patrimonial após o Fechamento
```
ATIVO                          | PASSIVO
------------------------------|-------------------------------
ATIVO CIRCULANTE      42.000  | PASSIVO CIRCULANTE     10.000
  Caixa               33.000  |   Fornecedores         10.000
  Estoque de Mercad.   9.000  |
                              | PASSIVO NÃO CIRCULANTE     0
ATIVO NÃO CIRCULANTE  20.000  |
  Equipamentos        20.000  | PATRIMÔNIO LÍQUIDO    52.000
                              |   Capital Social      50.000
                              |   Lucros Acumulados    2.000
------------------------------|-------------------------------
TOTAL                 62.000  | TOTAL                 62.000
```

## Caso 4: Análise Financeira

### Cenário
A diretoria da empresa "Comércio Modelo Ltda." solicita uma análise financeira para avaliar o desempenho e a saúde financeira da empresa.

### Índices Financeiros Calculados pelo Sistema

1. **Índices de Liquidez**
   ```
   Liquidez Corrente = Ativo Circulante / Passivo Circulante
   Liquidez Corrente = 42.000 / 10.000 = 4,2
   
   Liquidez Seca = (Ativo Circulante - Estoques) / Passivo Circulante
   Liquidez Seca = (42.000 - 9.000) / 10.000 = 3,3
   ```

2. **Índices de Endividamento**
   ```
   Grau de Endividamento = Passivo Total / Patrimônio Líquido
   Grau de Endividamento = 10.000 / 52.000 = 0,19 (19%)
   
   Composição do Endividamento = Passivo Circulante / Passivo Total
   Composição do Endividamento = 10.000 / 10.000 = 1,0 (100%)
   ```

3. **Índices de Rentabilidade**
   ```
   Margem Líquida = Lucro Líquido / Receita Líquida
   Margem Líquida = 2.000 / 10.000 = 0,20 (20%)
   
   Retorno sobre o Patrimônio Líquido = Lucro Líquido / Patrimônio Líquido
   Retorno sobre o PL = 2.000 / 52.000 = 0,038 (3,8%)
   ```

### Interpretação dos Resultados

1. **Liquidez**
   - A empresa possui excelente liquidez, com capacidade de pagar suas dívidas de curto prazo mais de 4 vezes
   - Mesmo desconsiderando os estoques, a empresa mantém boa liquidez (3,3)

2. **Endividamento**
   - O nível de endividamento é baixo (19% do patrimônio líquido)
   - Todo o endividamento está concentrado no curto prazo (fornecedores)

3. **Rentabilidade**
   - A margem líquida de 20% é considerada boa para empresas comerciais
   - O retorno sobre o patrimônio líquido ainda é baixo (3,8%), mas isso é comum em empresas recém-abertas

### Recomendações Baseadas na Análise
1. Considerar a utilização do caixa disponível para:
   - Ampliar os estoques e aumentar a capacidade de vendas
   - Investir em marketing para aumentar o volume de negócios
   - Negociar descontos com fornecedores para pagamentos à vista

2. Avaliar a possibilidade de diversificar a linha de produtos para aumentar a receita

3. Implementar controles de custos mais rigorosos para melhorar a margem de lucro

## Caso 5: Depreciação e Provisões

### Cenário
Após 6 meses de operação, a empresa precisa registrar a depreciação dos equipamentos (10% ao ano) e criar uma provisão para devedores duvidosos (5% sobre o saldo de clientes de R$ 8.000,00).

### Lançamentos Contábeis

1. **Registro da Depreciação Semestral**
   ```
   Débito: 5.1.2.05 - Despesas com Depreciação - R$ 1.000,00
   Crédito: 1.2.3.04 - (-) Depreciação Acumulada - R$ 1.000,00
   Histórico: Registro da depreciação semestral dos equipamentos
   
   Cálculo: R$ 20.000,00 x 10% / 2 = R$ 1.000,00
   ```

2. **Criação da Provisão para Devedores Duvidosos**
   ```
   Débito: 5.1.2.06 - Despesas com PDD - R$ 400,00
   Crédito: 1.1.2.02 - (-) Provisão para Devedores Duvidosos - R$ 400,00
   Histórico: Constituição de provisão para devedores duvidosos
   
   Cálculo: R$ 8.000,00 x 5% = R$ 400,00
   ```

### Impacto no Balanço Patrimonial
```
ATIVO                          | PASSIVO
------------------------------|-------------------------------
ATIVO CIRCULANTE      49.600  | PASSIVO CIRCULANTE     10.000
  Caixa               33.000  |   Fornecedores         10.000
  Clientes             8.000  |
  (-) PDD               -400  | PASSIVO NÃO CIRCULANTE     0
  Estoque de Mercad.   9.000  |
                              | PATRIMÔNIO LÍQUIDO    58.600
ATIVO NÃO CIRCULANTE  19.000  |   Capital Social      50.000
  Equipamentos        20.000  |   Lucros Acumulados    8.600
  (-) Depreciação     -1.000  |
------------------------------|-------------------------------
TOTAL                 68.600  | TOTAL                 68.600
```

---

## Dicas para Uso Educacional

1. **Utilize os Exemplos como Base**
   - Os casos apresentados podem ser usados como ponto de partida para exercícios mais complexos
   - Modifique os valores e adicione novas transações para criar variações

2. **Crie Cenários Completos**
   - Desenvolva um cenário de negócio completo, desde a abertura até o fechamento do ano fiscal
   - Inclua diferentes tipos de transações para cobrir diversos conceitos contábeis

3. **Explore os Relatórios**
   - Após registrar os lançamentos, gere diferentes relatórios para analisar os resultados
   - Compare os relatórios gerados pelo sistema com cálculos manuais para verificar a compreensão

4. **Trabalhe com Análises**
   - Utilize os dados gerados para calcular índices financeiros
   - Interprete os resultados e proponha ações de melhoria para a empresa fictícia

---

*Este documento de exemplos práticos complementa a documentação principal do Sistema de Contabilidade Educacional e deve ser utilizado como material de apoio para o ensino e aprendizagem de contabilidade.*
