from grupo_andrade import app, db
from grupo_andrade.models import User, Placa

# with app.app_context():
#     placas = Placa.query.all()
#     for placa in placas:
#         print(placa.author.username)


# print(placas)


with app.app_context():
    db.create_all()
    print('tabelas criadas')