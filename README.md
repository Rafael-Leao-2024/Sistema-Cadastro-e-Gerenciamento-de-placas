# link do projeto na web

https://web-production-7e591.up.railway.app/

# Grupo Andrade - Sistema de Gerenciamento de Placas

Este projeto é uma aplicação web desenvolvida em Flask para gerenciamento de placas. Ele permite aos usuários se cadastrarem, gerenciarem suas placas e consultarem informações relacionadas.

## Funcionalidades

- Registro de usuários e autenticação.
- Solicitação e gerenciamento de placas.
- Consulta e edição de placas cadastradas.
- Upload de imagens de perfil.
- Recuperação de senha via e-mail.
- Listagem de usuários.
- Paginação para exibição de placas e usuários.
- Controle de permissões para ações restritas.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Flask**: Framework web utilizado.
- **SQLAlchemy**: ORM para manipulação do banco de dados.
- **Flask-Login**: Gerenciamento de sessões e autenticação.
- **Flask-WTF**: Formulários seguros com validação.
- **Flask-Mail**: Envio de e-mails.
- **Pillow**: Manipulação de imagens.
- **Mercado Pago SDK**: Integração para pagamentos.

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio

   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt

   ```

4. Configure as variáveis de ambiente:

Crie um arquivo .env com suas configurações (e-mail, banco de dados, secret keys, etc).

5. Inicie o servidor:

```bash
 python run.py
```

## Estrutura do Projeto

```arduino

grupo_andrade/
├── __init__.py
├── forms.py
├── models.py
├── utilidades.py
├── static/
│   ├── profile_pics/
│   └── ...
├── templates/
│   ├── homepage.html
│   ├── login.html
│   ├── register.html
│   └── ...
└── routes.py
run.py
requirements.txt
README.md
```
