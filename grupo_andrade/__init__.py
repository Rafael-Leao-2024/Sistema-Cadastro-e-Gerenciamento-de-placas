from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from grupo_andrade.utilidades import format_data, format_hora, format_data_completa

app = Flask(__name__)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'suachavesecretabvvavdvBDABUSYNJBUBWBBBYQ')
#app.config['SECRET_KEY'] = 'suachavesecretabvvavdvBDABUSYNJBUBWBBBYQ'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.jinja_env.filters['format_data'] = format_data
app.jinja_env.filters['format_hora'] = format_hora
app.jinja_env.filters['format_data_completa'] = format_data_completa



# Verifica se a variável de ambiente DATABASE_URL existe

# Caso esteja em produção (Railway), usará o banco de dados configurado no Railway

# Caso contrário, usará o SQLite local
if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    # Para desenvolvimento local, use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'

# Configura o modo de depuração dependendo do ambiente
DEBUG = os.getenv('DEBUG', 'True') == 'True'
app.config['DEBUG'] = DEBUG

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

migrate = Migrate(app, db)


login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from . import routes

print('banco onlina desligado no local')
print(os.getenv('DATABASE_URL'))
