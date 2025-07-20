from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Message
from grupo_andrade.main import app, db, bcrypt
from sqlalchemy.orm import joinedload
from dotenv import load_dotenv
from sqlalchemy import extract
from sqlalchemy import desc
from datetime import datetime, timedelta
from PIL import Image
import mercadopago
import secrets
import os
from grupo_andrade.form import (RegistrationForm, EmplacamentoForm, LoginForm, EnderecoForm,\
                                ResetPasswordForm, UpdateAccountForm, ConsultarForm, RequestResetForm,\
                                PlacaStatusForm)
from grupo_andrade.models import User, Placa, Endereco, Pagamento
from grupo_andrade.utilidades import enviar_email, pegar_status, verificar_email
from grupo_andrade.main import mail

load_dotenv()
 

@app.route("/")
def homepage():
    return render_template('main/homepage.html', titulo='homepage')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash(f'{current_user.username} voce ja esta logado e no Home page', 'success')
        return redirect(url_for('homepage'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user != None:    
            senha_usuario = bcrypt.check_password_hash(user.password, form.password.data)     
        if user != None and senha_usuario == True:
            login_user(user)
            next_page = request.args.get('next')
            antes = request.full_path
            flash(f'User {user.username.title()} connected online', 'success')
            return redirect(next_page or url_for('solicitar_placas'))
        else:
            flash('email e senha invalido', 'danger')
            return redirect(url_for('login')) 
    return render_template('auth/login.html', form=form, titulo='login')

@app.route("/logout")
def logout():
    logout_user()
    flash(f'Voce esta desconectado', 'error')
    return redirect(url_for('login'))


@app.route("/minhas-placas")
@login_required
def minhas_placas():
    with app.app_context():
        per_page = 10
        page = request.args.get('page', 1, type=int)
        if current_user.is_authenticated:
            placas = Placa.query.options(joinedload(Placa.author))\
                       .filter_by(id_user=current_user.id)\
                       .order_by(desc(Placa.date_create))\
                       .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('placa/minhas_placas.html', placas=placas, titulo='minhas placas')


@app.route("/todas")
def todas():
    with app.app_context():
        per_page = 10
        page = request.args.get('page', 1, type=int)
        placas = Placa.query.options(joinedload(Placa.author))\
                        .order_by(desc(Placa.date_create))\
                        .paginate(page=page, per_page=per_page, error_out=False)
        total_placas = Placa.query.count()
    return render_template('placa/todas.html', placas=placas, total_placas=total_placas, titulo='todas')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        flash(f'{current_user.username} Voce ja esta logado e resgristrado pode postar', 'info')
        return redirect(url_for('postagem'))
    if form.validate_on_submit():
        if verificar_email(form.email.data):
            user = User.query.filter_by(email= form.email.data).first()
        else:
            flash(f'Este email nao é permitido use email valido!', 'info')
            return redirect(url_for('register')) 
        if user is None:
            senha_criptografada = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=senha_criptografada)
            db.session.add(user)
            db.session.commit() 
            flash(f'Account created for {user.username} Success!', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Username e Email ja exiti por favor escolha outros', 'info')
            return redirect(url_for('register')) 
    return render_template('auth/register.html', form=form, titulo='register')


@app.route('/minhas-placas/<int:placa_id>', methods=['GET', 'POST'])
@login_required
def placa_detail(placa_id):
    form = EmplacamentoForm()
    placa = Placa.query.get_or_404(placa_id)
    if not placa.id_user == current_user.id and not current_user.username == "admin":
        return render_template('erros/erro.html')
    if request.method == 'POST':
        received = request.form.get('received') == 'on'

        if received and not placa.received:
            placa.received = True
            placa.received_at = datetime.now()
            flash(f"Placa {placa.placa.upper()} Recebida com sucesso.", 'success')
        elif not received and placa.received:
            time_limit = placa.received_at + timedelta(minutes=10)
            if datetime.now() <= time_limit:
                placa.received = False
                placa.received_at = None  
            else:
                flash("Não é possível desmarcar após 10 minutos.", 'info')
        db.session.commit()
        
        return redirect(url_for('placa_detail', placa_id=placa.id))   
    return render_template('placa/placa_detail.html', placa=placa, form=form, titulo='detalhes')

@app.route("/minhas-placas/<int:placa_id>/delete", methods=['GET', 'POST'])
@login_required
def delete(placa_id):
    placa = Placa.query.get_or_404(placa_id)

    if placa.author != current_user and current_user.email != "rafaelampaz6@gmail.com":
        flash("Você não tem permissão para deletar esta placa.", "warning")
        return redirect(url_for('minhas_placas'))

    time_limit = placa.date_create + timedelta(hours=24)
    if datetime.now() > time_limit:
        flash("Você só pode deletar placas criadas há menos de 24 horas.", "error")
        return redirect(url_for('minhas_placas'))

    db.session.delete(placa)
    db.session.commit()
    flash(f'Sua placa {placa.placa.upper()} foi deletada!', 'success')
    return redirect(url_for('minhas_placas'))


@app.route('/endereco', methods=['GET', 'POST'])
@login_required
def endereco():
    form = EnderecoForm()
    if request.method == 'POST':
        endereco = request.form['endereco']
        novo_endereco = Endereco(endereco=endereco, id_user=current_user.id)
        db.session.add(novo_endereco)
        db.session.commit()
        flash('Endereço Atualizado com Sucesso!', 'success')
        return redirect(url_for('endereco'))
    elif request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        if endereco:
            form.endereco.data = endereco.endereco.title()
        else:
            form.endereco.data = Endereco.endereco.default.arg
    return render_template('user/endereco.html', form=form, endereco=endereco)


@app.route('/usuarios')
def listar_usuarios():
    usuarios = User.query.order_by(User.id.desc()).all()
    return render_template('user/listar_usuarios.html', usuarios=usuarios)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    imagem = Image.open(form_picture)
    imagem.thumbnail(output_size)
    imagem.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('user/account.html', title='Account', form=form, image_file=image_file)


@app.route('/consulta', methods=['GET', 'POST'])
@login_required
def consulta():
    resultados = []
    form = ConsultarForm()
    if request.method == 'POST':
        placa = request.form.get('placa')
        placa = placa.upper()
        if placa:
            resultados = Placa.query.filter(Placa.placa.ilike(f"%{placa}%")).order_by(Placa.date_create.desc()).all()
            if not resultados:
                flash("Placa não encontrada!", "warning")
            else:
                flash(f"Resultados Encontrados {len(resultados)}", "success")
    return render_template('placa/consulta.html', resultados=resultados, form=form)


@app.route('/editar/<int:placa_id>', methods=['GET', 'POST'])
@login_required
def editar_placa(placa_id):
    placa = Placa.query.get_or_404(placa_id)

    # Verifica se o usuário é o autor da placa
    if placa.id_user != current_user.id and current_user.email != "rafaelampaz6@gmail.com":
        flash("Você não tem permissão para editar esta placa.", "danger")
        return redirect(url_for('placa_detail' , placa_id=placa.id))

    if request.method == 'POST':
        placa.placa = request.form.get('placa')
        placa.renavan = request.form.get('renavan')
        placa.endereco_placa = request.form.get('endereco_placa')
        placa.crlv = request.form.get('crlv')
        db.session.commit()
        flash(f"Os dados da placa {placa.placa.upper()} foram atualizados com sucesso!", "success")
        return redirect(url_for('placa_detail', placa_id=placa.id))

    return render_template('placa/editar_placa.html', placa=placa)


def enviar_email_senha(user):
    token = user.get_reset_token()
    mensagem = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    mensagem.body = f'''Para redefinir sua senha, visite o seguinte link::
{url_for('reset_token', token=token, _external=True)}
Se você não fez esta solicitação, simplesmente ignore este e-mail e nenhuma alteração será feita.
obrigado {user.username}
'''
    mail.send(mensagem)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        enviar_email_senha(user)
        flash('Um e-mail foi enviado com instruções para redefinir sua senha.', 'info')
        return redirect(url_for('login'))
    return render_template('auth/reset_request.html', title='Reset Password', form=form)



@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Sua senha foi atualizada! Agora você pode fazer login', 'success')
        return redirect(url_for('login'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)


@app.route("/relatorio", methods=["GET", "POST"])
@login_required
def relatorio():
    if request.method == "POST":
        # Capturar o mês e o ano do formulário
        mes = int(request.form.get("mes"))
        ano = int(request.form.get("ano"))
        # Redirecionar para a rota de resultados com os parâmetros
        return redirect(url_for("relatorio_resultados", mes=mes, ano=ano))
    
    # Renderizar o formulário na primeira exibição
    return render_template("pagamento/relatorio_form.html")


    

@app.route("/relatorio/<int:mes>/<int:ano>")
@login_required
def relatorio_resultados(mes, ano):
    # Filtrar placas do usuário logado pelo mês e ano
    placas = Placa.query.filter(
        Placa.id_user == current_user.id,
        extract("month", Placa.date_create) == mes,
        extract("year", Placa.date_create) == ano
    ).all()
    # Calcular quantidade e valor total
    quantidade = len(placas)
    valor_total = quantidade * 100
    valor_total_str = f'{valor_total:,.2f}'
    # Criar a preferência de pagamento no Mercado Pago
    PROD_ACCESS_TOKEN = os.environ.get('PROD_ACCESS_TOKEN')
    sdk = mercadopago.SDK(PROD_ACCESS_TOKEN)
    
    link_resposta_pagamento = "https://web-production-7e591.up.railway.app/resultado_pagamento"
    preference_data = {
        "items": [
            {   "id": current_user.id,
                "title": f"Pagamento de {quantidade} placas",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": valor_total,
            }
        ],
        "back_urls": {
            "success": link_resposta_pagamento,
            "failure": link_resposta_pagamento,
            "pending": link_resposta_pagamento,
        },

        "auto_return": "all",
        "notification_url": "https://web-production-7e591.up.railway.app/",  # Adicione esta linha
    }

    preference_response = sdk.preference().create(preference_data)
    try:
        init_point = preference_response["response"]["init_point"]
    except:
        init_point = '/'
    return render_template("pagamento/relatorio_resultados.html", placas=placas, mes=mes, ano=ano, quantidade=quantidade,valor_total=valor_total_str,init_point=init_point)


@app.route('/resultado_pagamento')
@login_required
def resultado_pagamento():
    status_pagamento = request.args.get('status')
    id_usuario = current_user.id  
    id_pagamento = request.args.get('payment_id')

    if  id_pagamento == 'null':
        flash('Voce desistiu do pagamento caso queira falar com suporte chame no zap', 'warning')
        return redirect(url_for('relatorio'))        

    valor_pago, id_pagamento, status_pagamento = pegar_status(id_pagamento)
    novo_pagamento = Pagamento(
        id_pagamento=id_pagamento,
        status_pagamento=status_pagamento,
        id_usuario=id_usuario
    )
    db.session.add(novo_pagamento)
    db.session.commit() 

    if novo_pagamento.status_pagamento == 'approved':
        flash(f'Pagamento de R$ {valor_pago:,.2f} realizado com sucesso', 'success')
    return render_template('pagamento/resultado_pagamento.html', status_pagamento=status_pagamento)


@app.route('/solicitar_placas', methods=['GET', 'POST'])
@login_required
def solicitar_placas():
    if request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        try:
            endereco = endereco.endereco.title()
        except:
            endereco = Endereco.endereco.default.arg
    
    if request.method == 'POST':
        placas = request.form.getlist('placa') 
        enderecos = request.form.getlist('endereco_placa') 
        crlvs = request.form.getlist('crlv')
        renavams = request.form.getlist('renavam')

        lista_placas = []
        for placa, endereco, crlv, renavam in zip(placas, enderecos, crlvs, renavams):
            nova_placa = Placa(
                placa=placa.upper(),
                endereco_placa=endereco, 
                crlv=crlv, renavan=renavam,
                id_user=current_user.id
                )
            db.session.add(nova_placa)
            lista_placas.append(nova_placa)        
        db.session.commit()
        
        user = current_user
        if len(lista_placas) > 0:
            enviar_email(user, lista_placas)      
            flash('Placas solicitadas com sucesso e e-mail enviado!', 'success')
            return redirect(url_for('minhas_placas'))
        else:
            flash('Voce não preencheu os campos com os dados!', 'info')
            return redirect(url_for('solicitar_placas'))        
    return render_template('placa/solicitar_placas.html', titulo='solicitar varias placas', endereco=endereco)

@app.route("/gerenciamento-pedidos")
@login_required
def gerenciamento_pedidos():
    page = request.args.get('page', 1, type=int)
    placas = Placa.query.options(joinedload(Placa.author))\
                       .order_by(desc(Placa.date_create))\
                       .paginate(page=page, per_page=10, error_out=False)

    form = PlacaStatusForm()
    return render_template('placa/status_manager_placas.html', placas=placas, titulo='gerenciamento', tamanho=placas.total, form=form, page=page)

    
def pegar_pagina(url):
    try:
        indice = url.index("=")
        numero = url[indice + 1:]
    except:
        numero = 1
    return numero


@app.route("/gerenciamento-pedidos/<int:id_placa>", methods=['GET', 'POST'])
@login_required
def gerenciamento_final(id_placa):
    form = PlacaStatusForm()
    placa = Placa.query.filter(Placa.id==id_placa).first()
    page = int(pegar_pagina(dict(request.headers).get('Referer')))
    
    if request.method == "POST" and current_user.username == "admin":
        if form.placa_confeccionada.data:
            placa.placa_confeccionada = form.placa_confeccionada.data
        if form.placa_a_caminho.data:
            placa.placa_confeccionada = True
            placa.placa_a_caminho = form.placa_a_caminho.data
        db.session.commit()
    else:
        flash(category="info", message="Voce nao tem permissao de ADMIN")   
    return redirect(url_for('gerenciamento_pedidos', page=page))

