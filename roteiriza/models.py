from roteiriza import database, login_manager
from flask_login import UserMixin


class Entregas(database.Model):
    __tablename__ = 'entregas'
    id = database.Column(database.Integer, primary_key=True)
    data_recebido = database.Column(database.DateTime, nullable=False)
    descricao = database.Column(database.String(50))
    telefone = database.Column(database.String(12), nullable=False)
    tamanho_grande = database.Column(database.Boolean, nullable=False)
    endereco = database.Column(database.String(200), nullable=False)
    bairro = database.Column(database.String(100), nullable=False)
    latitude = database.Column(database.Float, nullable=False)
    longitude = database.Column(database.Float, nullable=False)


class Veiculos(database.Model):
    __tablename__ = 'veiculos'
    id = database.Column(database.Integer, primary_key=True)
    placa = database.Column(database.String(9), nullable=False)
    apelido = database.Column(database.String(50))
    cap_grande = database.Column(database.Boolean, nullable=False)


class Configuracoes(database.Model):
    __tablename__ = 'configuracoes'
    id = database.Column(database.Integer, primary_key=True)
    cap_moto = database.Column(database.Integer, nullable=False)
    cap_carros = database.Column(database.Integer, nullable=False)
    tempo_total = database.Column(database.Integer, nullable=False)
    tempo_entrega = database.Column(database.Integer, nullable=False)
    endereco_sede = database.Column(database.String(200), nullable=False)
    bairro_sede = database.Column(database.String(100), nullable=False)
    sede_lat = database.Column(database.Float, nullable=False)
    sede_long = database.Column(database.Float, nullable=False)


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    __tablename__ = 'usuario'
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<Usuario %r>' % self.nome
