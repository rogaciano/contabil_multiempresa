# Guia Visual do Sistema de Contabilidade Educacional

Este guia visual complementa a documentação principal do sistema, fornecendo representações visuais dos principais componentes e fluxos de trabalho.

## Estrutura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                        SISTEMA CONTÁBIL                         │
│                                                                 │
├───────────────┬───────────────┬───────────────┬────────────────┤
│               │               │               │                │
│   EMPRESAS    │  ANOS FISCAIS │  PLANO DE     │  LANÇAMENTOS   │
│               │               │   CONTAS      │                │
│               │               │               │                │
├───────────────┴───────────────┴───────────────┴────────────────┤
│                                                                 │
│                          RELATÓRIOS                             │
│                                                                 │
├─────────────┬─────────────┬────────────┬──────────┬────────────┤
│             │             │            │          │            │
│   BALANÇO   │    DRE      │   FLUXO    │BALANCETE │   RAZÃO    │
│ PATRIMONIAL │             │  DE CAIXA  │          │            │
│             │             │            │          │            │
└─────────────┴─────────────┴────────────┴──────────┴────────────┘
```

## Ciclo Contábil

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  Cadastro   │────▶│ Lançamentos │────▶│ Verificação │────▶│ Relatórios  │
│  Inicial    │     │  Contábeis  │     │ (Balancete) │     │ Financeiros │
│             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                                                           │
       │                                                           │
       └───────────────────────┐                 ┌─────────────────┘
                               ▼                 ▼
                         ┌─────────────────────────────┐
                         │                             │
                         │    Fechamento do Período    │
                         │                             │
                         └─────────────────────────────┘
```

## Estrutura de Contas (Exemplo)

```
1. ATIVO
   1.1. ATIVO CIRCULANTE
      1.1.1. Disponível
         1.1.1.01. Caixa
         1.1.1.02. Bancos Conta Movimento
      1.1.2. Créditos
         1.1.2.01. Clientes
         1.1.2.02. (-) Provisão para Devedores Duvidosos
   1.2. ATIVO NÃO CIRCULANTE
      1.2.1. Realizável a Longo Prazo
      1.2.2. Investimentos
      1.2.3. Imobilizado
         1.2.3.01. Móveis e Utensílios
         1.2.3.02. (-) Depreciação Acumulada

2. PASSIVO
   2.1. PASSIVO CIRCULANTE
      2.1.1. Fornecedores
      2.1.2. Obrigações Trabalhistas
   2.2. PASSIVO NÃO CIRCULANTE
      2.2.1. Empréstimos e Financiamentos

3. PATRIMÔNIO LÍQUIDO
   3.1. Capital Social
   3.2. Reservas
   3.3. Lucros/Prejuízos Acumulados

4. RECEITAS
   4.1. Receitas Operacionais
      4.1.1. Vendas de Mercadorias
      4.1.2. Prestação de Serviços
   4.2. Receitas Não Operacionais
      4.2.1. Receitas Financeiras

5. DESPESAS
   5.1. Despesas Operacionais
      5.1.1. Despesas Administrativas
      5.1.2. Despesas com Vendas
   5.2. Despesas Não Operacionais
      5.2.1. Despesas Financeiras
```

## Exemplo de Lançamento Contábil

### Compra de Mercadorias a Prazo

```
┌───────────────────────────────────────────────────────────────────┐
│ Data: 15/03/2025                                                  │
│ Histórico: Compra de mercadorias a prazo conforme NF 12345        │
├───────────────────────────────────────┬───────────┬───────────────┤
│ Conta                                 │   Débito  │    Crédito    │
├───────────────────────────────────────┼───────────┼───────────────┤
│ 1.1.3.01 - Estoque de Mercadorias     │ 5.000,00  │               │
│ 2.1.1.01 - Fornecedores               │           │    5.000,00   │
└───────────────────────────────────────┴───────────┴───────────────┘
```

## Exemplo de Balanço Patrimonial

```
┌───────────────────────────────────────────────────────────────────┐
│                       BALANÇO PATRIMONIAL                         │
│                          31/12/2025                               │
├───────────────────────────────┬───────────────────────────────────┤
│ ATIVO                         │ PASSIVO                           │
├───────────────────────────────┼───────────────────────────────────┤
│ ATIVO CIRCULANTE      25.000  │ PASSIVO CIRCULANTE        15.000  │
│   Caixa               10.000  │   Fornecedores            12.000  │
│   Bancos               8.000  │   Obrigações Trabalhistas  3.000  │
│   Clientes             7.000  │                                   │
│                               │ PASSIVO NÃO CIRCULANTE    10.000  │
│ ATIVO NÃO CIRCULANTE  35.000  │   Empréstimos             10.000  │
│   Imobilizado         40.000  │                                   │
│   (-) Depreciação     -5.000  │ PATRIMÔNIO LÍQUIDO        35.000  │
│                               │   Capital Social          30.000  │
│                               │   Lucros Acumulados        5.000  │
├───────────────────────────────┼───────────────────────────────────┤
│ TOTAL                 60.000  │ TOTAL                     60.000  │
└───────────────────────────────┴───────────────────────────────────┘
```

## Exemplo de DRE (Demonstração do Resultado do Exercício)

```
┌───────────────────────────────────────────────────────────────────┐
│                 DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO            │
│                    01/01/2025 a 31/12/2025                        │
├───────────────────────────────────────────────────┬───────────────┤
│ RECEITA BRUTA                                     │     50.000,00 │
│   Vendas de Mercadorias                           │     40.000,00 │
│   Prestação de Serviços                           │     10.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (-) DEDUÇÕES DA RECEITA                           │      5.000,00 │
│   Impostos sobre Vendas                           │      5.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (=) RECEITA LÍQUIDA                               │     45.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (-) CUSTO DAS MERCADORIAS VENDIDAS                │     20.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (=) LUCRO BRUTO                                   │     25.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (-) DESPESAS OPERACIONAIS                         │     18.000,00 │
│   Despesas Administrativas                        │     10.000,00 │
│   Despesas com Vendas                             │      5.000,00 │
│   Despesas Financeiras                            │      3.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (=) LUCRO OPERACIONAL                             │      7.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (+/-) RECEITAS/DESPESAS NÃO OPERACIONAIS          │      1.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (=) LUCRO ANTES DO IMPOSTO DE RENDA               │      8.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (-) PROVISÃO PARA IMPOSTO DE RENDA                │      3.000,00 │
├───────────────────────────────────────────────────┼───────────────┤
│ (=) LUCRO LÍQUIDO DO EXERCÍCIO                    │      5.000,00 │
└───────────────────────────────────────────────────┴───────────────┘
```

## Fluxo de Trabalho do Usuário

1. **Login no Sistema**
   ```
   [Tela de Login] → [Dashboard Principal]
   ```

2. **Seleção de Empresa**
   ```
   [Lista de Empresas] → [Selecionar Empresa] → [Dashboard da Empresa]
   ```

3. **Registro de Lançamento**
   ```
   [Menu] → [Lançamentos] → [Novo Lançamento] → [Preencher Dados] → [Salvar]
   ```

4. **Geração de Relatório**
   ```
   [Menu] → [Relatórios] → [Selecionar Relatório] → [Definir Parâmetros] → [Gerar]
   ```

5. **Fechamento de Ano Fiscal**
   ```
   [Menu] → [Anos Fiscais] → [Selecionar Ano] → [Fechar Ano] → [Confirmar]
   ```

## Recomendações para Uso Educacional

1. **Iniciar com Exemplos Simples**
   - Começar com lançamentos básicos (compras, vendas, pagamentos)
   - Verificar o balancete após cada lançamento para entender os efeitos

2. **Progressão Gradual**
   - Avançar para operações mais complexas (depreciação, provisões)
   - Explorar os diferentes relatórios e sua interpretação

3. **Projetos Práticos**
   - Simular a contabilidade completa de uma empresa por um período
   - Analisar os resultados e propor melhorias na gestão

---

*Nota: Este guia visual deve ser utilizado em conjunto com o documento principal "Sistema de Contabilidade Educacional" para uma compreensão completa do sistema.*
