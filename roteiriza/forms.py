from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, BooleanField, IntegerField, HiddenField, PasswordField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Email, Length, EqualTo
from flask_wtf.file import FileRequired, FileField, FileAllowed
from datetime import date
from roteiriza.models import Usuario
from roteiriza import token
from flask import flash


token_conf = token

class FormAdicionar(FlaskForm):
    data_recebido = DateField('Data de entrada:', default=date.today, validators=[DataRequired('Precisa ser preenchido')])
    descricao = StringField('Descrição:')
    telefone = IntegerField('Telefone:', validators=[DataRequired('Precisa ser preenchido'), NumberRange(min=1111111111, max=99999999999, message='2 digitos no DDD, 9 se tiver e 8 digitos')])
    tamanho_grande = BooleanField('Item Grande:')
    endereco = StringField('Endereço:', validators=[DataRequired('Precisa ser preenchido')])
    bairro = StringField('Bairro:', validators=[DataRequired('Precisa ser preenchido')])
    botao_adicionar = SubmitField('Adicionar')


class FormExluir(FlaskForm):
    id_excluir = HiddenField('Id Excluir:', name='id_excluir', validators=[DataRequired('')])
    botao_excluir = SubmitField('Excluir')


class FormExluirTudo(FlaskForm):
    botao_excluir_tudo = SubmitField('Excluir')


class FormPlanilha(FlaskForm):
    planilha = FileField('Planilha:', validators=[FileRequired(message='Precisa anexar a planilha'), FileAllowed(['xlsx'])])
    botao_planilha = SubmitField('Confirmar')


class FormEditarEntrega(FlaskForm):
    data_recebido = DateField('Data:', validators=[DataRequired('Precisa ser preenchido')])
    descricao = StringField('Descrição:')
    telefone = IntegerField('Telefone:', validators=[DataRequired('Precisa ser preenchido'), NumberRange(min=1111111111, max=99999999999, message='2 digitos no DDD, 9 se tiver e 8 digitos')])
    endereco = StringField('Endereço:', validators=[DataRequired('Precisa ser preenchido')])
    bairro = StringField('Bairro:', validators=[DataRequired('Precisa ser preenchido')])
    tamanho_grande = BooleanField('Item Grande:')
    botao_alterar = SubmitField('Alterar')


class FormAdicionarVeiculo(FlaskForm):
    placa = StringField('Placa:', validators=[DataRequired('Precisa ser preenchido')])
    apelido = StringField('Apelido:')
    cap_grande = BooleanField('Capacidade grande:')
    botao_adicionar = SubmitField('Adicionar')


class FormEditarVeiculo(FlaskForm):
    placa = StringField('Placa:', validators=[DataRequired('Precisa ser preenchido')])
    apelido = StringField('Apelido:')
    cap_grande = BooleanField('Capacidade grande:')
    botao_alterar = SubmitField('Alterar')


class FormConfiguracao(FlaskForm):
    cap_carros = IntegerField('Capacidade do Furgão*:', validators=[DataRequired('Precisa ser preenchido')])
    cap_moto = IntegerField('Capacidade da Moto*:', validators=[DataRequired('Precisa ser preenchido')])
    tempo_total = IntegerField('Tempo do Expediente*:', validators=[DataRequired('Precisa ser preenchido')])
    tempo_entrega = IntegerField('Tempo Médio por Entrega*:', validators=[DataRequired('Precisa ser preenchido')])
    endereco_sede = StringField('Endereço da sede:', validators=[DataRequired('Precisa ser preenchido')])
    bairro_sede = StringField('Bairro da sede:', validators=[DataRequired('Precisa ser preenchido')])
    botao_config = SubmitField('Salvar')


class FormLogin(FlaskForm):
    email_login = StringField('Email', validators=[DataRequired(message="Digite um email válido."), Email(message="Email inválido.")])
    senha_login = PasswordField('Senha', validators=[DataRequired(message="Digite uma senha válida."), Length(8, 20)])
    lembrar_senha = BooleanField('Manter conectado')
    botao_submit_login = SubmitField('Login')


class FormCadastroUsuario(FlaskForm):
    email_acesso = StringField('Email', validators=[DataRequired(message="Digite um email válido."), Email(message="Email inválido.")])
    senha_acesso = PasswordField('Senha', validators=[DataRequired(message="Digite uma senha válida."), Length(8, 20)])
    confirmacao_senha = PasswordField('Confirmação de Senha', validators=[DataRequired(message="Repita a senha."), Length(8, 20), EqualTo('senha_acesso', message="As senhas precisam ser iguais.")])
    token = StringField('Token', validators=[DataRequired(message="Cole o Token de validação interna.")])
    botao_submit_criar = SubmitField('Criar acesso')

    def validate_email_acesso(self, email_acesso):
        usuario = Usuario.query.filter_by(email=email_acesso.data).first()
        if usuario:
            raise ValidationError('Email Já cadastrado.')

    def validate_token(self, token):
        if token.data != token_conf:
            raise ValidationError('Token incorreto.')
