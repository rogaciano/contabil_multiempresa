# Generated by Django 5.0.2 on 2025-03-16 09:57

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_company_tax_regime'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DREReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_date', models.DateField(verbose_name='Data Inicial')),
                ('end_date', models.DateField(verbose_name='Data Final')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('notes', models.TextField(blank=True, verbose_name='Observações')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dre_reports', to='accounts.company', verbose_name='Empresa')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dre_reports', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Relatório DRE',
                'verbose_name_plural': 'Relatórios DRE',
                'ordering': ['-end_date', 'company'],
            },
        ),
        migrations.CreateModel(
            name='DREReportItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('is_subtotal', models.BooleanField(default=False, verbose_name='É subtotal')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor')),
                ('section_id', models.UUIDField(blank=True, null=True, verbose_name='ID da Seção Original')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='financial_reports.drereportitem', verbose_name='Item pai')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='financial_reports.drereport', verbose_name='Relatório')),
            ],
            options={
                'verbose_name': 'Item do Relatório DRE',
                'verbose_name_plural': 'Itens do Relatório DRE',
                'ordering': ['report', 'order'],
            },
        ),
        migrations.CreateModel(
            name='DRESection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('is_subtotal', models.BooleanField(default=False, help_text='Indica se esta seção representa um subtotal', verbose_name='É subtotal')),
                ('formula', models.TextField(blank=True, help_text='Fórmula para calcular o valor desta seção (se for subtotal)', verbose_name='Fórmula')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='financial_reports.dresection', verbose_name='Seção pai')),
            ],
            options={
                'verbose_name': 'Seção do DRE',
                'verbose_name_plural': 'Seções do DRE',
                'ordering': ['template', 'order'],
            },
        ),
        migrations.CreateModel(
            name='DREAccount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('account_type', models.CharField(help_text='Tipo ou código da conta contábil a ser incluída nesta seção', max_length=20, verbose_name='Tipo de Conta')),
                ('multiplier', models.IntegerField(default=1, help_text='1 para adicionar o valor da conta, -1 para subtrair', verbose_name='Multiplicador')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='financial_reports.dresection', verbose_name='Seção')),
            ],
            options={
                'verbose_name': 'Conta do DRE',
                'verbose_name_plural': 'Contas do DRE',
                'ordering': ['section', 'account_type'],
            },
        ),
        migrations.CreateModel(
            name='DRETemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('tax_regime', models.CharField(choices=[('SN', 'Simples Nacional'), ('LR', 'Lucro Real'), ('LP', 'Lucro Presumido')], help_text='Regime tributário para o qual este template de DRE é aplicável', max_length=2, verbose_name='Regime Tributário')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
            ],
            options={
                'verbose_name': 'Template de DRE',
                'verbose_name_plural': 'Templates de DRE',
                'ordering': ['tax_regime', 'name'],
                'unique_together': {('tax_regime', 'name')},
            },
        ),
        migrations.AddField(
            model_name='dresection',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='financial_reports.dretemplate', verbose_name='Template'),
        ),
        migrations.AddField(
            model_name='drereport',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports', to='financial_reports.dretemplate', verbose_name='Template'),
        ),
    ]
