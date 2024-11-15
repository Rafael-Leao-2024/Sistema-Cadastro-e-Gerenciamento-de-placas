from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SECRET_KEY'] = 'suachavesecretabvvavdvBDABUSYNJBUBWBBBYQ'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

migrate = Migrate(app, db)


login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from . import routes




