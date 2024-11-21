import os
import pickle

from sqlalchemy import text
from roteiriza import app, database, bcrypt
from flask import render_template, send_file, request, url_for, redirect, flash
from flask_login import login_required, login_user, logout_user
from .models import Entregas, Veiculos, Configuracoes, Usuario
from .forms import FormAdicionar, FormAdicionarVeiculo, FormEditarEntrega, FormEditarVeiculo, FormPlanilha, FormExluir, FormConfiguracao, FormExluirTudo, FormLogin, FormCadastroUsuario
from .functions.end_to_coord import coordenadas
from .functions.save_sheets import adic_planilha
from .functions.roteirizar import roteirizar


def atualizar_configuracao(config, form_configuracoes):
    atributos = {
        'cap_moto': 'cap_moto',
        'cap_carros': 'cap_carros',
        'tempo_total': 'tempo_total',
        'tempo_entrega': 'tempo_entrega',
        'endereco_sede': 'endereco_sede',
        'bairro_sede': 'bairro_sede'
    }
    for attr_form, attr_config in atributos.items():
        setattr(config, attr_config, getattr(form_configuracoes, attr_form).data)
    end_completo = f'{form_configuracoes.endereco_sede.data} - {form_configuracoes.bairro_sede.data}, Teresina, Piauí'
    coord = coordenadas(end_completo)
    config.sede_lat = coord['lat']
    config.sede_long = coord['lng']
    database.session.commit()
    return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    titulo = "Página Inicial"
    arquivo = os.path.exists(f'roteiriza/templates/mapas/arquivo.pkl')

    config = Configuracoes.query.get(1)
    form_configuracoes = FormConfiguracao()
    if form_configuracoes.validate_on_submit() and 'botao_config' in request.form:
        atualizar_configuracao(config, form_configuracoes)

    if 'botao-att-rotas' in request.form:
        veiculos = Veiculos.query.all()
        dados_vei = [[item.id, item.cap_grande] for item in veiculos]
        roteirizar(config, dados_vei)
        return redirect(url_for('resumo'))

    return render_template("./home/home.html", titulo=titulo, arquivo=arquivo, config=config, form_configuracoes=form_configuracoes, zip=zip)


@app.route('/objetos', methods=['GET', 'POST'])
@login_required
def objetos():
    titulo = "Objetos/Itens de entrega"
    entregas = Entregas.query.all()
    arquivo = os.path.exists(f'roteiriza/templates/mapas/arquivo.pkl')

    # Form Adicionar (convertendo o endereço em coordenadas)
    form_adicionar = FormAdicionar()
    if form_adicionar.validate_on_submit() and 'botao_adicionar' in request.form:
        end_completo = f'{form_adicionar.endereco.data} - {form_adicionar.bairro.data}, Teresina, Piauí'
        coord = coordenadas(end_completo)
        entrega = Entregas(
            data_recebido=form_adicionar.data_recebido.data,
            descricao=form_adicionar.descricao.data,
            telefone=form_adicionar.telefone.data,
            tamanho_grande=form_adicionar.tamanho_grande.data,
            endereco=form_adicionar.endereco.data,
            bairro=form_adicionar.bairro.data,
            latitude=coord['lat'],
            longitude=coord['lng']
        )
        database.session.add(entrega)
        database.session.commit()
        return redirect(url_for('objetos'))

    # Form Editar
    form_editar_entrega = FormEditarEntrega()
    if form_editar_entrega.validate_on_submit() and 'botao_alterar' in request.form:
        id_editar = request.form.get('id-form-editar')
        entrega = Entregas.query.get(id_editar)
        entrega.data_recebido = form_editar_entrega.data_recebido.data
        entrega.descricao = form_editar_entrega.descricao.data
        entrega.telefone = form_editar_entrega.telefone.data
        entrega.tamanho_grande = form_editar_entrega.tamanho_grande.data
        entrega.endereco = form_editar_entrega.endereco.data
        entrega.bairro = form_editar_entrega.bairro.data
        end_completo = f'{form_editar_entrega.endereco.data} - {form_editar_entrega.bairro.data}, Teresina, Piauí'
        coord = coordenadas(end_completo)
        entrega.latitude = coord['lat']
        entrega.longitude = coord['lng']

        database.session.commit()
        return redirect(url_for('objetos'))

    form_planilha = FormPlanilha()
    if form_planilha.validate_on_submit() and 'botao_planilha' in request.form:
        caminho = os.path.join(app.root_path, 'static/files', 'planilha.xlsx')
        if os.path.exists(caminho):
            os.remove(caminho)
        planilha = form_planilha.planilha.data
        planilha.save(caminho)
        adic_planilha()

        return redirect(url_for('objetos'))

    form_excluir = FormExluir()
    if form_excluir.validate_on_submit() and 'botao_excluir' in request.form:
        id_excluir = request.form.get('id_excluir')
        entrega = Entregas.query.get(id_excluir)
        database.session.delete(entrega)
        database.session.commit()
        return redirect(url_for('objetos'))

    config = Configuracoes.query.get(1)
    form_configuracoes = FormConfiguracao()
    if form_configuracoes.validate_on_submit() and 'botao_config' in request.form:
        atualizar_configuracao(config, form_configuracoes)

    form_excluir_tudo = FormExluirTudo()
    if form_excluir_tudo.validate_on_submit() and 'botao_excluir_tudo' in request.form:
        Entregas.query.delete()
        database.session.execute(text("ALTER SEQUENCE entregas_id_seq RESTART WITH 1"))
        database.session.commit()
        return redirect(url_for('objetos'))

    if 'botao-att-rotas' in request.form:
        veiculos = Veiculos.query.all()
        dados_vei = [[item.id, item.cap_grande] for item in veiculos]
        roteirizar(config, dados_vei)
        return redirect(url_for('resumo'))

    return render_template('objetos.html', titulo=titulo, arquivo=arquivo, entregas=entregas, form_adicionar=form_adicionar, form_editar_entrega=form_editar_entrega, form_excluir=form_excluir, form_excluir_tudo=form_excluir_tudo, form_planilha=form_planilha, form_configuracoes=form_configuracoes, config=config, zip=zip)


@app.route('/veiculos', methods=['GET', 'POST'])
@login_required
def veiculos():
    titulo = "Veículos disponíveis"
    # Form Adicionar
    form_adicionar = FormAdicionarVeiculo()
    arquivo = os.path.exists(f'roteiriza/templates/mapas/arquivo.pkl')

    if form_adicionar.validate_on_submit() and 'botao_adicionar' in request.form:
        veiculo = Veiculos(
            placa=form_adicionar.placa.data,
            apelido=form_adicionar.apelido.data,
            cap_grande=form_adicionar.cap_grande.data
        )
        database.session.add(veiculo)
        database.session.commit()
        return redirect(url_for('veiculos'))

    # Form Editar
    form_editar_veiculo = FormEditarVeiculo()
    if form_editar_veiculo.validate_on_submit() and 'botao_alterar' in request.form:
        id_editar = request.form.get('id-form-editar')
        veiculo = Veiculos.query.get(id_editar)
        veiculo.placa = form_editar_veiculo.placa.data
        veiculo.apelido = form_editar_veiculo.apelido.data
        veiculo.cap_grande = form_editar_veiculo.cap_grande.data

        database.session.commit()
        return redirect(url_for('veiculos'))

    form_excluir = FormExluir()
    if form_excluir.validate_on_submit() and 'botao_excluir' in request.form:
        id_excluir = request.form.get('id_excluir')
        rota = Veiculos.query.get(id_excluir)
        database.session.delete(rota)
        database.session.commit()
        return redirect(url_for('veiculos'))

    form_excluir_tudo = FormExluirTudo()
    if form_excluir_tudo.validate_on_submit() and 'botao_excluir_tudo' in request.form:
        Veiculos.query.delete()
        database.session.execute(text("ALTER SEQUENCE veiculos_id_seq RESTART WITH 1"))
        database.session.commit()

        return redirect(url_for('veiculos'))

    config = Configuracoes.query.get(1)
    form_configuracoes = FormConfiguracao()
    if form_configuracoes.validate_on_submit() and 'botao_config' in request.form:
        atualizar_configuracao(config, form_configuracoes)

    veiculos = Veiculos.query.all()

    if 'botao-att-rotas' in request.form:
        dados_vei = [[item.id, item.cap_grande] for item in veiculos]
        roteirizar(config, dados_vei)
        return redirect(url_for('resumo'))

    return render_template('./veiculos/veiculos.html', titulo=titulo, arquivo=arquivo, veiculos=veiculos, form_adicionar=form_adicionar, form_editar_veiculo=form_editar_veiculo, form_excluir=form_excluir, form_excluir_tudo=form_excluir_tudo, form_configuracoes=form_configuracoes, config=config, zip=zip)


@app.route('/download', methods=['GET'])
@login_required
def download():
    planilha = os.path.join(app.root_path, 'static/files', 'entregas.xlsx')
    return send_file(planilha)


@app.route('/mapa_<veiculo>', methods=['GET'])
@login_required
def mapa(veiculo):
    if not os.path.exists(f'roteiriza/templates/mapas/mapa_{veiculo}.html'):
        return 'Não existe rota para exibir'
    return render_template(f'./mapas/mapa_{veiculo}.html')


@app.route('/resumo', methods=['GET'])
@login_required
def resumo():
    try:
        with open('roteiriza/templates/mapas/arquivo.pkl', 'rb') as file:
            dados = pickle.load(file)

            n_veiculos = len(dados)
            km_total = sum(valor[0] for valor in dados.values()) / 1000
            entregas_total = sum(len(valor[1]) for valor in dados.values())
            info_veiculos = {veiculo.id: veiculo for veiculo in
                             database.session.query(Veiculos).filter(Veiculos.id.in_(dados.keys())).all()}
            entregas = {entrega.id: entrega for entrega in database.session.query(Entregas).filter(
                Entregas.id.in_([parada for sublist in dados.values() for parada in sublist[1]])).all()}

            return render_template('resumo.html', enumerate=enumerate, dados=dados, info_veiculos=info_veiculos, entregas=entregas, km_total=km_total, entregas_total=entregas_total, n_veiculos=n_veiculos)
    except FileNotFoundError:
        return 'Não existem rotas para resumir'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email_login.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha_login.data):
            login_user(usuario, remember=form_login.lembrar_senha)
            flash(f'Login feito com sucesso! Bem vindo, o e-mail logado é: {form_login.email_login.data}',
                  'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash('Falha no login! E-mail ou senha incorretos.', 'alert-danger')

    return render_template('login/login.html', form_login=form_login)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form_cadastro = FormCadastroUsuario()
    if form_cadastro.validate_on_submit() and 'botao_submit_criar' in request.form:
        senha_crypt = bcrypt.generate_password_hash(form_cadastro.senha_acesso.data).decode('utf-8')
        usuario = Usuario(email=form_cadastro.email_acesso.data, senha=senha_crypt)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Novo acesso criado com sucesso para o e-mail: {form_cadastro.email_acesso.data}', 'alert-success')
        return redirect(url_for('login'))
    return render_template('login/cadastro.html', form_cadastro=form_cadastro)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout Feito com Sucesso', 'alert-success')
    return redirect(url_for('login'))

