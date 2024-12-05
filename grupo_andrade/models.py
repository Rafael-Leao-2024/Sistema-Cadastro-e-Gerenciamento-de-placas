from grupo_andrade import db
from datetime import datetime
from grupo_andrade import login_manager
from flask_login import UserMixin
from datetime import datetime



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='padrao.png')
    password = db.Column(db.String(80), nullable=False)
    placas = db.relationship('Placa', backref='author', lazy=True)

    def __repr__(self):
        return f" User(username={self.username}, email={self.email})"

class Placa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(80), unique=False, nullable=False)
    renavan = db.Column(db.String(120), unique=False, nullable=False)
    endereco_placa = db.Column(db.String(120), unique=False, nullable=False)
    crlv = db.Column(db.String(80), nullable=False)
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.now)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    received = db.Column(db.Boolean, default=False)
    received_at = db.Column(db.DateTime, nullable=True, default=datetime.now)  # Hora da confirmação
        
    def __repr__(self):
        return f"Placa(placa={self.placa})"
    

class Endereco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endereco = db.Column(db.String(255), nullable=True, default='Nenhum Endereço')  # Campo de endereço
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # FK para User

    def __repr__(self):
        return f"Endereco(endereco={self.endereco})"
