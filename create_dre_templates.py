import os
import sys
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabil.settings')
django.setup()

# Importar os modelos após configurar o Django
from financial_reports.models import DRETemplate, DRESection
from accounts.models import Company

def create_dre_templates():
    print("Iniciando criação dos templates DRE...")
    
    # Limpar tabelas existentes
    print("Limpando tabelas existentes...")
    DRESection.objects.all().delete()
    DRETemplate.objects.all().delete()
    print("Tabelas limpas com sucesso!")
    
    # Criar templates
    print("Criando templates...")
    sn_template = DRETemplate.objects.create(
        name='DRE - Simples Nacional',
        description='Template de DRE para empresas do Simples Nacional',
        tax_regime=Company.TaxRegime.SIMPLES_NACIONAL,
        is_active=True
    )
    
    lr_template = DRETemplate.objects.create(
        name='DRE - Lucro Real',
        description='Template de DRE para empresas do Lucro Real',
        tax_regime=Company.TaxRegime.LUCRO_REAL,
        is_active=True
    )
    
    lp_template = DRETemplate.objects.create(
        name='DRE - Lucro Presumido',
        description='Template de DRE para empresas do Lucro Presumido',
        tax_regime=Company.TaxRegime.LUCRO_PRESUMIDO,
        is_active=True
    )
    print("Templates criados com sucesso!")
    
    # Criar seções para o template do Simples Nacional
    print("Criando seções para o template do Simples Nacional...")
    
    # 1. Receita Bruta
    sn_receita_bruta = DRESection.objects.create(
        template=sn_template,
        name='Receita Bruta',
        description='Receita bruta total',
        order=10,
        is_subtotal=False
    )
    
    # 2. Deduções da Receita
    sn_deducoes = DRESection.objects.create(
        template=sn_template,
        name='Deduções da Receita',
        description='Deduções da receita bruta',
        order=20,
        is_subtotal=False
    )
    
    # 3. Receita Líquida (Subtotal)
    sn_receita_liquida = DRESection.objects.create(
        template=sn_template,
        name='Receita Líquida',
        description='Receita bruta menos deduções',
        order=30,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    sn_receita_liquida.formula = f'{sn_receita_bruta.id} - {sn_deducoes.id}'
    sn_receita_liquida.save()
    
    # 4. Custo das Mercadorias Vendidas (CMV) / Custo dos Serviços Prestados (CSP)
    sn_cmv_csp = DRESection.objects.create(
        template=sn_template,
        name='CMV / CSP',
        description='Custo das Mercadorias Vendidas ou Custo dos Serviços Prestados',
        order=40,
        is_subtotal=False
    )
    
    # 5. Lucro Bruto (Subtotal)
    sn_lucro_bruto = DRESection.objects.create(
        template=sn_template,
        name='Lucro Bruto',
        description='Receita líquida menos custos',
        order=50,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    sn_lucro_bruto.formula = f'{sn_receita_liquida.id} - {sn_cmv_csp.id}'
    sn_lucro_bruto.save()
    
    # 6. Despesas Operacionais
    sn_despesas_operacionais = DRESection.objects.create(
        template=sn_template,
        name='Despesas Operacionais',
        description='Despesas relacionadas à operação',
        order=60,
        is_subtotal=False
    )
    
    # 7. Resultado Operacional (Subtotal)
    sn_resultado_operacional = DRESection.objects.create(
        template=sn_template,
        name='Resultado Operacional',
        description='Lucro bruto menos despesas operacionais',
        order=70,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    sn_resultado_operacional.formula = f'{sn_lucro_bruto.id} - {sn_despesas_operacionais.id}'
    sn_resultado_operacional.save()
    
    # 8. Receitas Financeiras
    sn_receitas_financeiras = DRESection.objects.create(
        template=sn_template,
        name='Receitas Financeiras',
        description='Receitas de aplicações financeiras e outras',
        order=80,
        is_subtotal=False
    )
    
    # 9. Despesas Financeiras
    sn_despesas_financeiras = DRESection.objects.create(
        template=sn_template,
        name='Despesas Financeiras',
        description='Juros, tarifas bancárias e outras despesas financeiras',
        order=90,
        is_subtotal=False
    )
    
    # 10. Resultado Financeiro (Subtotal)
    sn_resultado_financeiro = DRESection.objects.create(
        template=sn_template,
        name='Resultado Financeiro',
        description='Receitas financeiras menos despesas financeiras',
        order=100,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    sn_resultado_financeiro.formula = f'{sn_receitas_financeiras.id} - {sn_despesas_financeiras.id}'
    sn_resultado_financeiro.save()
    
    # 11. Resultado Antes do Simples Nacional (Subtotal)
    sn_resultado_antes_impostos = DRESection.objects.create(
        template=sn_template,
        name='Resultado Antes do Simples Nacional',
        description='Resultado operacional mais resultado financeiro',
        order=110,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    sn_resultado_antes_impostos.formula = f'{sn_resultado_operacional.id} + {sn_resultado_financeiro.id}'
    sn_resultado_antes_impostos.save()
    
    # 12. Simples Nacional
    sn_simples_nacional = DRESection.objects.create(
        template=sn_template,
        name='Simples Nacional',
        description='Imposto unificado do Simples Nacional',
        order=120,
        is_subtotal=False
    )
    
    # 13. Lucro Líquido do Exercício (Subtotal)
    sn_lucro_liquido = DRESection.objects.create(
        template=sn_template,
        name='Lucro Líquido do Exercício',
        description='Resultado final após impostos',
        order=130,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    sn_lucro_liquido.formula = f'{sn_resultado_antes_impostos.id} - {sn_simples_nacional.id}'
    sn_lucro_liquido.save()
    
    print("Seções para o template do Simples Nacional criadas com sucesso!")
    
    # Criar seções para o template do Lucro Real
    print("Criando seções para o template do Lucro Real...")
    
    # 1. Receita Bruta
    lr_receita_bruta = DRESection.objects.create(
        template=lr_template,
        name='Receita Bruta',
        description='Receita bruta total',
        order=10,
        is_subtotal=False
    )
    
    # 2. Deduções da Receita
    lr_deducoes = DRESection.objects.create(
        template=lr_template,
        name='Deduções da Receita',
        description='Deduções da receita bruta',
        order=20,
        is_subtotal=False
    )
    
    # 3. Receita Líquida (Subtotal)
    lr_receita_liquida = DRESection.objects.create(
        template=lr_template,
        name='Receita Líquida',
        description='Receita bruta menos deduções',
        order=30,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lr_receita_liquida.formula = f'{lr_receita_bruta.id} - {lr_deducoes.id}'
    lr_receita_liquida.save()
    
    # 4. Custo das Mercadorias Vendidas (CMV) / Custo dos Serviços Prestados (CSP)
    lr_cmv_csp = DRESection.objects.create(
        template=lr_template,
        name='CMV / CSP',
        description='Custo das Mercadorias Vendidas ou Custo dos Serviços Prestados',
        order=40,
        is_subtotal=False
    )
    
    # 5. Lucro Bruto (Subtotal)
    lr_lucro_bruto = DRESection.objects.create(
        template=lr_template,
        name='Lucro Bruto',
        description='Receita líquida menos custos',
        order=50,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lr_lucro_bruto.formula = f'{lr_receita_liquida.id} - {lr_cmv_csp.id}'
    lr_lucro_bruto.save()
    
    # 6. Despesas Operacionais
    lr_despesas_operacionais = DRESection.objects.create(
        template=lr_template,
        name='Despesas Operacionais',
        description='Despesas relacionadas à operação',
        order=60,
        is_subtotal=False
    )
    
    # 7. Resultado Operacional (Subtotal)
    lr_resultado_operacional = DRESection.objects.create(
        template=lr_template,
        name='Resultado Operacional',
        description='Lucro bruto menos despesas operacionais',
        order=70,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lr_resultado_operacional.formula = f'{lr_lucro_bruto.id} - {lr_despesas_operacionais.id}'
    lr_resultado_operacional.save()
    
    # 8. Receitas Financeiras
    lr_receitas_financeiras = DRESection.objects.create(
        template=lr_template,
        name='Receitas Financeiras',
        description='Receitas de aplicações financeiras e outras',
        order=80,
        is_subtotal=False
    )
    
    # 9. Despesas Financeiras
    lr_despesas_financeiras = DRESection.objects.create(
        template=lr_template,
        name='Despesas Financeiras',
        description='Juros, tarifas bancárias e outras despesas financeiras',
        order=90,
        is_subtotal=False
    )
    
    # 10. Resultado Financeiro (Subtotal)
    lr_resultado_financeiro = DRESection.objects.create(
        template=lr_template,
        name='Resultado Financeiro',
        description='Receitas financeiras menos despesas financeiras',
        order=100,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lr_resultado_financeiro.formula = f'{lr_receitas_financeiras.id} - {lr_despesas_financeiras.id}'
    lr_resultado_financeiro.save()
    
    # 11. Resultado Antes dos Impostos (Subtotal)
    lr_resultado_antes_impostos = DRESection.objects.create(
        template=lr_template,
        name='Resultado Antes dos Impostos',
        description='Resultado operacional mais resultado financeiro',
        order=110,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lr_resultado_antes_impostos.formula = f'{lr_resultado_operacional.id} + {lr_resultado_financeiro.id}'
    lr_resultado_antes_impostos.save()
    
    # 12. IRPJ
    lr_irpj = DRESection.objects.create(
        template=lr_template,
        name='IRPJ',
        description='Imposto de Renda Pessoa Jurídica',
        order=120,
        is_subtotal=False
    )
    
    # 13. CSLL
    lr_csll = DRESection.objects.create(
        template=lr_template,
        name='CSLL',
        description='Contribuição Social sobre o Lucro Líquido',
        order=130,
        is_subtotal=False
    )
    
    # 14. Lucro Líquido do Exercício (Subtotal)
    lr_lucro_liquido = DRESection.objects.create(
        template=lr_template,
        name='Lucro Líquido do Exercício',
        description='Resultado final após impostos',
        order=140,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lr_lucro_liquido.formula = f'{lr_resultado_antes_impostos.id} - {lr_irpj.id} - {lr_csll.id}'
    lr_lucro_liquido.save()
    
    print("Seções para o template do Lucro Real criadas com sucesso!")
    
    # Criar seções para o template do Lucro Presumido
    print("Criando seções para o template do Lucro Presumido...")
    
    # 1. Receita Bruta
    lp_receita_bruta = DRESection.objects.create(
        template=lp_template,
        name='Receita Bruta',
        description='Receita bruta total',
        order=10,
        is_subtotal=False
    )
    
    # 2. Deduções da Receita
    lp_deducoes = DRESection.objects.create(
        template=lp_template,
        name='Deduções da Receita',
        description='Deduções da receita bruta',
        order=20,
        is_subtotal=False
    )
    
    # 3. Receita Líquida (Subtotal)
    lp_receita_liquida = DRESection.objects.create(
        template=lp_template,
        name='Receita Líquida',
        description='Receita bruta menos deduções',
        order=30,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lp_receita_liquida.formula = f'{lp_receita_bruta.id} - {lp_deducoes.id}'
    lp_receita_liquida.save()
    
    # 4. Custo das Mercadorias Vendidas (CMV) / Custo dos Serviços Prestados (CSP)
    lp_cmv_csp = DRESection.objects.create(
        template=lp_template,
        name='CMV / CSP',
        description='Custo das Mercadorias Vendidas ou Custo dos Serviços Prestados',
        order=40,
        is_subtotal=False
    )
    
    # 5. Lucro Bruto (Subtotal)
    lp_lucro_bruto = DRESection.objects.create(
        template=lp_template,
        name='Lucro Bruto',
        description='Receita líquida menos custos',
        order=50,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lp_lucro_bruto.formula = f'{lp_receita_liquida.id} - {lp_cmv_csp.id}'
    lp_lucro_bruto.save()
    
    # 6. Despesas Operacionais
    lp_despesas_operacionais = DRESection.objects.create(
        template=lp_template,
        name='Despesas Operacionais',
        description='Despesas relacionadas à operação',
        order=60,
        is_subtotal=False
    )
    
    # 7. Resultado Operacional (Subtotal)
    lp_resultado_operacional = DRESection.objects.create(
        template=lp_template,
        name='Resultado Operacional',
        description='Lucro bruto menos despesas operacionais',
        order=70,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lp_resultado_operacional.formula = f'{lp_lucro_bruto.id} - {lp_despesas_operacionais.id}'
    lp_resultado_operacional.save()
    
    # 8. Receitas Financeiras
    lp_receitas_financeiras = DRESection.objects.create(
        template=lp_template,
        name='Receitas Financeiras',
        description='Receitas de aplicações financeiras e outras',
        order=80,
        is_subtotal=False
    )
    
    # 9. Despesas Financeiras
    lp_despesas_financeiras = DRESection.objects.create(
        template=lp_template,
        name='Despesas Financeiras',
        description='Juros, tarifas bancárias e outras despesas financeiras',
        order=90,
        is_subtotal=False
    )
    
    # 10. Resultado Financeiro (Subtotal)
    lp_resultado_financeiro = DRESection.objects.create(
        template=lp_template,
        name='Resultado Financeiro',
        description='Receitas financeiras menos despesas financeiras',
        order=100,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lp_resultado_financeiro.formula = f'{lp_receitas_financeiras.id} - {lp_despesas_financeiras.id}'
    lp_resultado_financeiro.save()
    
    # 11. Resultado Antes dos Impostos (Subtotal)
    lp_resultado_antes_impostos = DRESection.objects.create(
        template=lp_template,
        name='Resultado Antes dos Impostos',
        description='Resultado operacional mais resultado financeiro',
        order=110,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lp_resultado_antes_impostos.formula = f'{lp_resultado_operacional.id} + {lp_resultado_financeiro.id}'
    lp_resultado_antes_impostos.save()
    
    # 12. PIS/COFINS
    lp_pis_cofins = DRESection.objects.create(
        template=lp_template,
        name='PIS/COFINS',
        description='PIS e COFINS sobre receita',
        order=120,
        is_subtotal=False
    )
    
    # 13. IRPJ Presumido
    lp_irpj = DRESection.objects.create(
        template=lp_template,
        name='IRPJ Presumido',
        description='Imposto de Renda Pessoa Jurídica pelo Lucro Presumido',
        order=130,
        is_subtotal=False
    )
    
    # 14. CSLL Presumido
    lp_csll = DRESection.objects.create(
        template=lp_template,
        name='CSLL Presumido',
        description='Contribuição Social sobre o Lucro Líquido pelo Lucro Presumido',
        order=140,
        is_subtotal=False
    )
    
    # 15. Lucro Líquido do Exercício (Subtotal)
    lp_lucro_liquido = DRESection.objects.create(
        template=lp_template,
        name='Lucro Líquido do Exercício',
        description='Resultado final após impostos',
        order=150,
        is_subtotal=True
    )
    
    # Atualizar fórmula
    lp_lucro_liquido.formula = f'{lp_resultado_antes_impostos.id} - {lp_pis_cofins.id} - {lp_irpj.id} - {lp_csll.id}'
    lp_lucro_liquido.save()
    
    print("Seções para o template do Lucro Presumido criadas com sucesso!")
    
    print("Todos os templates e seções foram criados com sucesso!")

if __name__ == "__main__":
    create_dre_templates()
