# Sistema de Contabilidade Educacional

## Visão Geral

O Sistema de Contabilidade Educacional é uma aplicação web desenvolvida para fins didáticos, destinada a auxiliar estudantes de contabilidade a compreender os conceitos fundamentais da contabilidade através de uma interface intuitiva e prática. Este sistema permite o gerenciamento completo de operações contábeis, incluindo múltiplas empresas, anos fiscais, plano de contas, lançamentos contábeis e geração de relatórios financeiros.

## Objetivo Educacional

Este sistema foi desenvolvido pelo Professor Rogaciano da Paz como uma ferramenta educacional para:

- Facilitar o aprendizado prático de contabilidade
- Demonstrar a aplicação dos princípios contábeis em um ambiente real
- Permitir que os alunos pratiquem o registro e análise de transações contábeis
- Visualizar como os relatórios financeiros são gerados a partir dos lançamentos contábeis

## Recursos Principais

### 1. Gerenciamento de Múltiplas Empresas

O sistema permite a criação e gerenciamento de múltiplas empresas, possibilitando que os estudantes pratiquem a contabilidade em diferentes contextos empresariais.

**Recursos:**
- Cadastro de empresas com informações completas (nome, CNPJ, endereço, etc.)
- Seleção da empresa ativa para trabalho
- Visualização detalhada dos dados da empresa

### 2. Gestão de Anos Fiscais

O sistema implementa o conceito de anos fiscais, permitindo a organização cronológica das operações contábeis.

**Recursos:**
- Criação de anos fiscais com datas de início e fim
- Fechamento de anos fiscais com transferência automática de saldos
- Visualização do status de cada ano fiscal (aberto/fechado)

### 3. Plano de Contas Hierárquico

Um plano de contas completo e hierárquico permite a organização estruturada das contas contábeis.

**Recursos:**
- Estrutura hierárquica de contas (até 5 níveis)
- Classificação por tipo (Ativo, Passivo, Patrimônio Líquido, Receita, Despesa)
- Contas sintéticas (agrupamento) e analíticas (lançamentos)
- Códigos de conta padronizados

### 4. Lançamentos Contábeis

O sistema permite o registro de lançamentos contábeis completos, respeitando o princípio do débito e crédito.

**Recursos:**
- Lançamentos com múltiplas partidas
- Validação automática do equilíbrio entre débitos e créditos
- Histórico detalhado para cada lançamento
- Anexos de documentos comprobatórios

### 5. Relatórios Financeiros

Uma série de relatórios financeiros permite a análise da situação patrimonial e de resultados da empresa.

**Relatórios disponíveis:**
- Balanço Patrimonial
- Demonstração do Resultado do Exercício (DRE)
- Fluxo de Caixa
- Balancete de Verificação
- Razão Geral

### 6. Painel de Controle

Um dashboard interativo apresenta informações resumidas sobre a situação financeira da empresa.

**Informações disponíveis:**
- Resumo de ativos e passivos
- Gráfico de receitas x despesas
- Indicadores financeiros chave
- Alertas sobre situações específicas

## Tecnologias Utilizadas

O sistema foi desenvolvido utilizando tecnologias modernas de desenvolvimento web:

- **Backend**: Django (Framework Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Estilização**: Tailwind CSS
- **Interatividade**: Alpine.js
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Gráficos**: Chart.js
- **Relatórios PDF**: xhtml2pdf

## Fluxo de Trabalho Típico

1. **Configuração Inicial**:
   - Cadastro de uma nova empresa
   - Criação de um ano fiscal
   - Configuração do plano de contas

2. **Operações Diárias**:
   - Registro de lançamentos contábeis
   - Consulta de saldos de contas
   - Verificação de balancetes

3. **Fechamento Mensal/Anual**:
   - Geração de relatórios financeiros
   - Análise de resultados
   - Fechamento do período contábil

## Exemplos de Uso

### Exemplo 1: Registro de uma Venda à Vista

1. Acesse o sistema e selecione a empresa desejada
2. Navegue até "Lançamentos" e clique em "Novo Lançamento"
3. Preencha a data e o histórico: "Venda de mercadorias à vista"
4. Adicione as partidas:
   - Débito em "Caixa" (1.1.1.01) - R$ 1.000,00
   - Crédito em "Receita de Vendas" (3.1.1.01) - R$ 1.000,00
5. Salve o lançamento

### Exemplo 2: Geração de um Balanço Patrimonial

1. Acesse o sistema e selecione a empresa desejada
2. Navegue até "Relatórios" > "Balanço Patrimonial"
3. Selecione o período desejado (por exemplo, 01/01/2025 a 31/12/2025)
4. Clique em "Gerar Relatório"
5. Visualize o Balanço Patrimonial na tela ou exporte para PDF

## Benefícios Educacionais

- **Aprendizado Prático**: Os estudantes podem aplicar conceitos teóricos em um ambiente real
- **Visualização Imediata**: Os efeitos dos lançamentos são imediatamente visíveis nos relatórios
- **Compreensão Sistêmica**: Entendimento de como os diferentes elementos contábeis se relacionam
- **Preparação Profissional**: Familiarização com sistemas contábeis similares aos utilizados no mercado

## Requisitos do Sistema

- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Conexão com a internet
- Resolução de tela mínima de 1024x768

## Suporte e Contato

Para suporte técnico ou dúvidas sobre o sistema, entre em contato com:

**Prof. Rogaciano da Paz**  
Telefone: (81) 9 9921-6560  
E-mail: [rogaciano@webpic.com.br](mailto:contato@rogacianodapaz.com.br)

---

*Este sistema é destinado exclusivamente para fins educacionais e não deve ser utilizado para contabilidade oficial ou fiscal de empresas reais sem as devidas adaptações e certificações.*
