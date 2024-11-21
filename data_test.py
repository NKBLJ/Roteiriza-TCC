from roteiriza import database, app
#
#
# with app.app_context():
#     database.create_all()
#     database.session.commit()


from roteiriza.models import Entregas, Veiculos

with app.app_context():
    veiculo = Veiculos.query.get(1)
    print(veiculo.cap_grande)
    print(veiculo.cap_grande == True)
    # print(entrega.descricao)
    # print(entrega.telefone)
    # print('Grande' if entrega.tamanho_grande else 'Pequeno')
    # print(entrega.endereco)
