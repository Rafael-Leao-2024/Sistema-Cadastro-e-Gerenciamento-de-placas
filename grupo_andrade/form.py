from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from grupo_andrade.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Repeat Password', validators=[ DataRequired(), EqualTo('password')])    
    submit = SubmitField('Submit')


# Defina o formulário de emplacamento
class EmplacamentoForm(FlaskForm):
    placa = StringField('Placa', validators=[DataRequired()])
    crlv = StringField('CRLV', validators=[DataRequired()])
    renavam = StringField('Renavam', validators=[DataRequired()])
    endereco_placa = StringField('endereco_placa', validators=[DataRequired()])
    received = BooleanField("Recebida", default=False)


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EnderecoForm(FlaskForm):
    endereco = StringField(
        'Endereço',
        validators=[
            DataRequired(message="O endereço é obrigatório."),
            Length(max=255, message="O endereço deve ter no máximo 255 caracteres.")
        ]
    )
    submit = SubmitField('Edite e Salve')
