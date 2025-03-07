# Sistema Contábil Django

Sistema contábil completo desenvolvido com Django, utilizando Tailwind CSS para uma interface moderna e responsiva.

## Requisitos

- Python 3.10+
- pip (gerenciador de pacotes Python)
- virtualenv (opcional, mas recomendado)

## Instalação

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd contabil_windsurf
```

2. Crie e ative um ambiente virtual (opcional):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto e adicione:
```
SECRET_KEY=sua-chave-secreta
DEBUG=True
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Instale e compile o Tailwind CSS:
```bash
python manage.py tailwind install
python manage.py tailwind build
```

7. Crie um superusuário:
```bash
python manage.py createsuperuser
```

8. Execute o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## Funcionalidades

- Gestão de contas contábeis
- Registro de transações financeiras
- Relatórios financeiros (Balanço Patrimonial, DRE, Fluxo de Caixa)
- Dashboard com indicadores financeiros
- Interface responsiva com Tailwind CSS
- Sistema de autenticação e autorização
- Exportação de relatórios

## Estrutura do Projeto

```
contabil/
├── core/               # Aplicação principal
├── accounts/          # Gestão de contas
├── transactions/      # Gestão de transações
├── reports/          # Relatórios financeiros
├── templates/        # Templates HTML
└── static/           # Arquivos estáticos
```

## Desenvolvimento

Para contribuir com o projeto:

1. Crie um branch para sua feature
2. Desenvolva e teste sua feature
3. Faça commit das alterações
4. Crie um pull request

## Licença

Este projeto está licenciado sob a licença MIT.
#   c o n t a b i l 
 
 #   c o n t a b i l 
 
 