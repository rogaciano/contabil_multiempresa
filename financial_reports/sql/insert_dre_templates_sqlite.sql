-- Script SQL para inserir templates de DRE e suas seções (versão SQLite)
-- Este script cria templates para os três regimes tributários: Simples Nacional (SN), Lucro Real (LR) e Lucro Presumido (LP)

-- Template para Simples Nacional
INSERT INTO financial_reports_dretemplate (id, name, description, tax_regime, is_active, created_at, updated_at)
VALUES 
('11111111-1111-1111-1111-111111111111', 'DRE Padrão - Simples Nacional', 'Template padrão de DRE para empresas do Simples Nacional', 'SN', 1, datetime('now'), datetime('now'));

-- Template para Lucro Real
INSERT INTO financial_reports_dretemplate (id, name, description, tax_regime, is_active, created_at, updated_at)
VALUES 
('22222222-2222-2222-2222-222222222222', 'DRE Padrão - Lucro Real', 'Template padrão de DRE para empresas do Lucro Real', 'LR', 1, datetime('now'), datetime('now'));

-- Template para Lucro Presumido
INSERT INTO financial_reports_dretemplate (id, name, description, tax_regime, is_active, created_at, updated_at)
VALUES 
('33333333-3333-3333-3333-333333333333', 'DRE Padrão - Lucro Presumido', 'Template padrão de DRE para empresas do Lucro Presumido', 'LP', 1, datetime('now'), datetime('now'));

-- Seções para o template do Simples Nacional
-- 1. Receita Bruta
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'Receita Bruta', 'Total das receitas brutas', 10, 0, NULL, NULL);

-- 2. Deduções da Receita
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a2222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Deduções da Receita', 'Deduções da receita bruta', 20, 0, NULL, NULL);

-- 3. Receita Líquida (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a3333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 'Receita Líquida', 'Receita bruta menos deduções', 30, 1, 'a1111111-1111-1111-1111-111111111111 - a2222222-2222-2222-2222-222222222222', NULL);

-- 4. Custo dos Produtos/Serviços
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a4444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 'Custo dos Produtos/Serviços', 'Custos diretos relacionados aos produtos ou serviços', 40, 0, NULL, NULL);

-- 5. Lucro Bruto (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a5555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', 'Lucro Bruto', 'Receita líquida menos custos', 50, 1, 'a3333333-3333-3333-3333-333333333333 - a4444444-4444-4444-4444-444444444444', NULL);

-- 6. Despesas Operacionais
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a6666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111', 'Despesas Operacionais', 'Despesas relacionadas à operação do negócio', 60, 0, NULL, NULL);

-- 7. Resultado Operacional (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a7777777-7777-7777-7777-777777777777', '11111111-1111-1111-1111-111111111111', 'Resultado Operacional', 'Lucro bruto menos despesas operacionais', 70, 1, 'a5555555-5555-5555-5555-555555555555 - a6666666-6666-6666-6666-666666666666', NULL);

-- 8. Receitas Financeiras
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a8888888-8888-8888-8888-888888888888', '11111111-1111-1111-1111-111111111111', 'Receitas Financeiras', 'Receitas de aplicações financeiras e juros recebidos', 80, 0, NULL, NULL);

-- 9. Despesas Financeiras
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('a9999999-9999-9999-9999-999999999999', '11111111-1111-1111-1111-111111111111', 'Despesas Financeiras', 'Juros, tarifas bancárias e outras despesas financeiras', 90, 0, NULL, NULL);

-- 10. Resultado Financeiro (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('aaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'Resultado Financeiro', 'Receitas financeiras menos despesas financeiras', 100, 1, 'a8888888-8888-8888-8888-888888888888 - a9999999-9999-9999-9999-999999999999', NULL);

-- 11. Resultado Antes do Simples Nacional (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('bbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', 'Resultado Antes do Simples Nacional', 'Resultado operacional mais resultado financeiro', 110, 1, 'a7777777-7777-7777-7777-777777777777 + aaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', NULL);

-- 12. Simples Nacional
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('ccccccc-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111', 'Simples Nacional', 'Imposto unificado do Simples Nacional', 120, 0, NULL, NULL);

-- 13. Lucro Líquido do Exercício (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('ddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111', 'Lucro Líquido do Exercício', 'Resultado final após impostos', 130, 1, 'bbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb - ccccccc-cccc-cccc-cccc-cccccccccccc', NULL);

-- Seções para o template do Lucro Real
-- 1. Receita Bruta
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b1111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Receita Bruta', 'Total das receitas brutas', 10, 0, NULL, NULL);

-- 2. Deduções da Receita
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 'Deduções da Receita', 'Deduções da receita bruta', 20, 0, NULL, NULL);

-- 3. Receita Líquida (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b3333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', 'Receita Líquida', 'Receita bruta menos deduções', 30, 1, 'b1111111-1111-1111-1111-111111111111 - b2222222-2222-2222-2222-222222222222', NULL);

-- 4. Custo dos Produtos/Serviços
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b4444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', 'Custo dos Produtos/Serviços', 'Custos diretos relacionados aos produtos ou serviços', 40, 0, NULL, NULL);

-- 5. Lucro Bruto (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b5555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', 'Lucro Bruto', 'Receita líquida menos custos', 50, 1, 'b3333333-3333-3333-3333-333333333333 - b4444444-4444-4444-4444-444444444444', NULL);

-- 6. Despesas Operacionais
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b6666666-6666-6666-6666-666666666666', '22222222-2222-2222-2222-222222222222', 'Despesas Operacionais', 'Despesas relacionadas à operação do negócio', 60, 0, NULL, NULL);

-- 7. Resultado Operacional (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b7777777-7777-7777-7777-777777777777', '22222222-2222-2222-2222-222222222222', 'Resultado Operacional', 'Lucro bruto menos despesas operacionais', 70, 1, 'b5555555-5555-5555-5555-555555555555 - b6666666-6666-6666-6666-666666666666', NULL);

-- 8. Receitas Financeiras
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b8888888-8888-8888-8888-888888888888', '22222222-2222-2222-2222-222222222222', 'Receitas Financeiras', 'Receitas de aplicações financeiras e juros recebidos', 80, 0, NULL, NULL);

-- 9. Despesas Financeiras
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('b9999999-9999-9999-9999-999999999999', '22222222-2222-2222-2222-222222222222', 'Despesas Financeiras', 'Juros, tarifas bancárias e outras despesas financeiras', 90, 0, NULL, NULL);

-- 10. Resultado Financeiro (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222', 'Resultado Financeiro', 'Receitas financeiras menos despesas financeiras', 100, 1, 'b8888888-8888-8888-8888-888888888888 - b9999999-9999-9999-9999-999999999999', NULL);

-- 11. Resultado Antes do IRPJ e CSLL (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('bccccccc-cccc-cccc-cccc-cccccccccccc', '22222222-2222-2222-2222-222222222222', 'Resultado Antes do IRPJ e CSLL', 'Resultado operacional mais resultado financeiro', 110, 1, 'b7777777-7777-7777-7777-777777777777 + bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', NULL);

-- 12. Provisão para IRPJ
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('bddddddd-dddd-dddd-dddd-dddddddddddd', '22222222-2222-2222-2222-222222222222', 'Provisão para IRPJ', 'Imposto de Renda Pessoa Jurídica', 120, 0, NULL, NULL);

-- 13. Provisão para CSLL
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('beeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '22222222-2222-2222-2222-222222222222', 'Provisão para CSLL', 'Contribuição Social sobre o Lucro Líquido', 130, 0, NULL, NULL);

-- 14. Lucro Líquido do Exercício (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('bfffffff-ffff-ffff-ffff-ffffffffffff', '22222222-2222-2222-2222-222222222222', 'Lucro Líquido do Exercício', 'Resultado final após impostos', 140, 1, 'bccccccc-cccc-cccc-cccc-cccccccccccc - bddddddd-dddd-dddd-dddd-dddddddddddd - beeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', NULL);

-- Seções para o template do Lucro Presumido
-- 1. Receita Bruta
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c1111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'Receita Bruta', 'Total das receitas brutas', 10, 0, NULL, NULL);

-- 2. Deduções da Receita
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c2222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', 'Deduções da Receita', 'Deduções da receita bruta', 20, 0, NULL, NULL);

-- 3. Receita Líquida (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c3333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', 'Receita Líquida', 'Receita bruta menos deduções', 30, 1, 'c1111111-1111-1111-1111-111111111111 - c2222222-2222-2222-2222-222222222222', NULL);

-- 4. Custo dos Produtos/Serviços
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c4444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', 'Custo dos Produtos/Serviços', 'Custos diretos relacionados aos produtos ou serviços', 40, 0, NULL, NULL);

-- 5. Lucro Bruto (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c5555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333333', 'Lucro Bruto', 'Receita líquida menos custos', 50, 1, 'c3333333-3333-3333-3333-333333333333 - c4444444-4444-4444-4444-444444444444', NULL);

-- 6. Despesas Operacionais
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c6666666-6666-6666-6666-666666666666', '33333333-3333-3333-3333-333333333333', 'Despesas Operacionais', 'Despesas relacionadas à operação do negócio', 60, 0, NULL, NULL);

-- 7. Resultado Operacional (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c7777777-7777-7777-7777-777777777777', '33333333-3333-3333-3333-333333333333', 'Resultado Operacional', 'Lucro bruto menos despesas operacionais', 70, 1, 'c5555555-5555-5555-5555-555555555555 - c6666666-6666-6666-6666-666666666666', NULL);

-- 8. Receitas Financeiras
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c8888888-8888-8888-8888-888888888888', '33333333-3333-3333-3333-333333333333', 'Receitas Financeiras', 'Receitas de aplicações financeiras e juros recebidos', 80, 0, NULL, NULL);

-- 9. Despesas Financeiras
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('c9999999-9999-9999-9999-999999999999', '33333333-3333-3333-3333-333333333333', 'Despesas Financeiras', 'Juros, tarifas bancárias e outras despesas financeiras', 90, 0, NULL, NULL);

-- 10. Resultado Financeiro (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('cccccccc-cccc-cccc-cccc-cccccccccccc', '33333333-3333-3333-3333-333333333333', 'Resultado Financeiro', 'Receitas financeiras menos despesas financeiras', 100, 1, 'c8888888-8888-8888-8888-888888888888 - c9999999-9999-9999-9999-999999999999', NULL);

-- 11. Resultado Antes dos Impostos (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('cddddddd-dddd-dddd-dddd-dddddddddddd', '33333333-3333-3333-3333-333333333333', 'Resultado Antes dos Impostos', 'Resultado operacional mais resultado financeiro', 110, 1, 'c7777777-7777-7777-7777-777777777777 + cccccccc-cccc-cccc-cccc-cccccccccccc', NULL);

-- 12. PIS/COFINS
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('ceeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '33333333-3333-3333-3333-333333333333', 'PIS/COFINS', 'PIS e COFINS sobre receita', 120, 0, NULL, NULL);

-- 13. IRPJ Presumido
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('cfffffff-ffff-ffff-ffff-ffffffffffff', '33333333-3333-3333-3333-333333333333', 'IRPJ Presumido', 'Imposto de Renda Pessoa Jurídica pelo Lucro Presumido', 130, 0, NULL, NULL);

-- 14. CSLL Presumido
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('cggggggg-gggg-gggg-gggg-gggggggggggg', '33333333-3333-3333-3333-333333333333', 'CSLL Presumido', 'Contribuição Social sobre o Lucro Líquido pelo Lucro Presumido', 140, 0, NULL, NULL);

-- 15. Lucro Líquido do Exercício (Subtotal)
INSERT INTO financial_reports_dresection (id, template_id, name, description, "order", is_subtotal, formula, parent_id)
VALUES 
('chhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhhh', '33333333-3333-3333-3333-333333333333', 'Lucro Líquido do Exercício', 'Resultado final após impostos', 150, 1, 'cddddddd-dddd-dddd-dddd-dddddddddddd - ceeeeeee-eeee-eeee-eeee-eeeeeeeeeeee - cfffffff-ffff-ffff-ffff-ffffffffffff - cggggggg-gggg-gggg-gggg-gggggggggggg', NULL);
