from grupo_andrade import app, DEBUG


import os
from flask import Flask
from flask_migrate import Migrate
from grupo_andrade import app, db  # Altere 'your_application' para o nome do seu módulo

# Configurações da aplicação
app = app

# Inicializa Flask-Migrate
migrate = Migrate(app, db)

def main():
    with app.app_context():
        # Aplica as migrações
        print("Iniciando migrações...")
        from flask_migrate import upgrade
        upgrade()
        print("Migrações aplicadas com sucesso!")



if __name__ == '__main__':
    app.run(debug=DEBUG)