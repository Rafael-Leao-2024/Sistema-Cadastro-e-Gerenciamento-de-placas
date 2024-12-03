from flask import render_template, redirect, url_for, flash, request, abort
from grupo_andrade.form import RegistrationForm, EmplacamentoForm, LoginForm, EnderecoForm, UpdateAccountForm, ConsultarForm
from grupo_andrade.models import User, Placa, Endereco
from flask_login import login_required, current_user, login_user, logout_user
from . import app, db, bcrypt
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import secrets
import os
from PIL import Image

@app.route("/")
def homepage():
    return render_template('homepage.html', titulo='homepage')

@app.route("/emplacar", methods=["GET", "POST"])
@login_required
def emplacamento():
    form = EmplacamentoForm()
    if request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        try:
            form.endereco_placa.data = endereco.endereco.title()
        except:
            form.endereco_placa.data = Endereco.endereco.default.arg
    if form.validate_on_submit():
        # Lógica para processar os dados do formulário
        placa = Placa(placa=form.placa.data.upper(), crlv=form.crlv.data, renavan=form.renavam.data, endereco_placa=form.endereco_placa.data, id_user=current_user.id)
        db.session.add(placa)
        db.session.commit() 
        flash(f'Placa {placa.placa.upper()} solicitada com Success!', 'success')
        # Exemplo: salvar no banco de dados ou fazer algo com os dados
        return redirect(url_for('minhas_placas'))
    return render_template('emplacar.html', form=form, titulo='emplacar')

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
            #placas = Placa.query.filter_by(id_user=current_user.id).order_by(desc(Placa.date_create)).paginate(page=page, per_page=per_page, error_out=False)
            # Carrega as placas do usuário logado, incluindo o relacionamento 'author'
            placas = Placa.query.options(joinedload(Placa.author))\
                       .filter_by(id_user=current_user.id)\
                       .order_by(desc(Placa.date_create))\
                       .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('minhas_placas.html', placas=placas, titulo='minhas placas')



@app.route("/todas")
def todas():
    with app.app_context():
        per_page = 10
        page = request.args.get('page', 1, type=int)
        # Busca todas as placas, sem filtro de usuário
        placas = Placa.query.options(joinedload(Placa.author))\
                        .order_by(desc(Placa.date_create))\
                        .paginate(page=page, per_page=per_page, error_out=False)
        # Conta o total de placas na base de dados
        total_placas = Placa.query.count()
    return render_template('todas.html', placas=placas, total_placas=total_placas, titulo='todas')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash(f'{current_user.username} voce ja esta logado e no Home page', 'success')
        return redirect(url_for('homepage'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user != None:    
            senha_usuario = bcrypt.check_password_hash(user.password, form.password.data) # returns True        
        if user != None and senha_usuario == True:
            login_user(user)            
            flash(f'User {user.username.title()} connected online', 'success')
            return redirect(url_for('emplacamento'))
        else:
            flash('email e senha invalido', 'danger')
            return redirect(url_for('login')) 
    return render_template('login.html', form=form, titulo='login')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        flash(f'{current_user.username} Voce ja esta logado e resgristrado pode postar', 'info')
        return redirect(url_for('postagem'))
    if form.validate_on_submit():
        user = User.query.filter_by(email= form.email.data).first()
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
    return render_template('register.html', form=form, titulo='register')


@app.route('/minhas-placas/<int:placa_id>', methods=['GET', 'POST'])
@login_required
def placa_detail(placa_id):
    # Busca a placa pelo ID
    form = EmplacamentoForm()
    placa = Placa.query.get_or_404(placa_id)

    # Verifica se o usuário logado é o dono da placa
    if placa.id_user != current_user.id:
        #abort(403)  # Ou redireciona para uma página de erro
        return render_template('erros/erro.html')

    if request.method == 'POST':
        # Verifica se a caixa de seleção foi marcada
        received = request.form.get('received') == 'on'

        if received and not placa.received:
            # Marca como recebido e define a data/hora atual
            placa.received = True
            placa.received_at = datetime.now()
            flash(f"Placa {placa.placa.upper()} Recebida com sucesso.", 'success')
        elif not received and placa.received:
            # Verifica se o tempo limite de 10 minutos já passou
            time_limit = placa.received_at + timedelta(minutes=10)
            if datetime.now() <= time_limit:
                placa.received = False
                placa.received_at = None  # Opcional: limpa o campo
            else:
                flash("Não é possível desmarcar após 10 minutos.", 'info')
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        return redirect(url_for('placa_detail', placa_id=placa.id))  # Redireciona para a mesma página para refletir a alteração
    
    return render_template('placa_detail.html', placa=placa, form=form, titulo='detalhes')


# rota de deletar postagem
@app.route("/minhas-placas/<int:placa_id>/delete", methods=['GET', 'POST'])
@login_required
def delete(placa_id):
    placa = Placa.query.get_or_404(placa_id)

    if placa.author != current_user:
        flash("Você não tem permissão para deletar esta placa.", "warning")
        return redirect(url_for('minhas_placas'))

    # Verifica se o tempo de 24 horas já passou
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
        return redirect(url_for('endereco'))  # Redireciona para a página inicial ou onde preferir
    elif request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        print(endereco)
        if endereco:
            form.endereco.data = endereco.endereco.title()
        else:
            form.endereco.data = Endereco.endereco.default.arg
    return render_template('endereco.html', form=form, endereco=endereco)


@app.route('/usuarios')
def listar_usuarios():

    usuarios = User.query.all()  # Consulta todos os usuários
    return render_template('listar_usuarios.html', usuarios=usuarios)



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

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
    return render_template('account.html', title='Account', form=form, image_file=image_file)



@app.route('/consulta', methods=['GET', 'POST'])
@login_required
def consulta():
    resultados = []
    form = ConsultarForm()
    if request.method == 'POST':
        placa = request.form.get('placa')
        placa = placa.upper()
        if placa:
            #resultado = Placa.query.filter_by(placa=placa).first()
            #resultado = Placa.query.filter(Placa.placa.ilike(f"%{placa}%")).all()
            resultados = Placa.query.filter(Placa.placa.ilike(f"%{placa}%")).order_by(Placa.date_create.desc()).all()
            if not resultados:
                flash("Placa não encontrada!", "warning")
            else:
                flash(f"Resultados Encontrados {len(resultados)}", "success")
    return render_template('consulta.html', resultados=resultados, form=form)


@app.route('/editar/<int:placa_id>', methods=['GET', 'POST'])
@login_required
def editar_placa(placa_id):
    placa = Placa.query.get_or_404(placa_id)

    # Verifica se o usuário é o autor da placa
    if placa.id_user != current_user.id:
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

    return render_template('editar_placa.html', placa=placa)
