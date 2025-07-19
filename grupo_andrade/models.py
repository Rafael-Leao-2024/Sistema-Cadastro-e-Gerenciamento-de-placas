from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from grupo_andrade.main import db, login_manager, app

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

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': str(self.id)})

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
    received_at = db.Column(db.DateTime, nullable=True, default=datetime.now)
    placa_confeccionada = db.Column(db.Boolean, default=False)
    placa_a_caminho = db.Column(db.Boolean, default=False)
        
    def __repr__(self):
        return f"Placa(placa={self.placa})"
    

class Endereco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endereco = db.Column(db.String(255), nullable=True, default='Nenhum Endereço')
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  

    def __repr__(self):
        return f"Endereco(endereco={self.endereco})"


class Pagamento(db.Model):
    __tablename__ = 'pagamento'  

    id = db.Column(db.Integer, primary_key=True)  # ID do pagamento
    id_pagamento = db.Column(db.String(255), unique=False, nullable=False)  
    status_pagamento = db.Column(db.String(50), nullable=False)  
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_pagamento = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'<Pagamento {self.id} - {self.status_pagamento}>'
    


