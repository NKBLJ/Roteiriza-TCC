import folium
import os
import shutil
import pickle
from roteiriza.models import Entregas
from datetime import datetime
import requests
import openrouteservice as ors
from sqlalchemy import desc
import io
from PIL import Image


def carregar_dados(local_arquivo):
    try:
        with open(local_arquivo, 'rb') as arquivo:
            dados = pickle.load(arquivo)
    except FileNotFoundError:
        dados = dict([])
    return dados


def add_markers_and_polylines(mapa, veiculos, completo=False):
    colors = ['black', 'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'darkblue', 'lightblue',
         'darkgreen', 'lightgreen', 'cadetblue', 'gray', 'white', 'pink', 'brown', 'yellow', 'cyan', 'magenta',
         'olive', 'lime', 'teal', 'navy', 'maroon', 'silver', 'gold', 'indigo', 'violet', 'turquoise', 'plum',
         'salmon', 'tan', 'lavender', 'khaki', 'coral', 'aquamarine', 'bisque', 'chartreuse', 'darkcyan',
         'darkmagenta', 'darkorange', 'darkviolet', 'deeppink', 'lightpink', 'lightsalmon', 'lightseagreen',
         'mediumaquamarine', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise',
         'mediumvioletred', 'palegreen', 'paleturquoise', 'peachpuff', 'rosybrown', 'royalblue', 'saddlebrown',
         'seagreen', 'sienna', 'slateblue', 'slategray', 'springgreen', 'steelblue', 'thistle', 'tomato', 'wheat',
         'yellowgreen']
    for veiculo in veiculos:
        i = 0
        for pontos in veiculo['steps'][1:-1]:
            i += 1
            popup = folium.Popup(str(i), parse_html=True)
            folium.Marker(location=list(reversed(pontos['location'])), popup=popup).add_to(mapa)
        color = colors[veiculo['vehicle']]  # Escolha de cor baseada no índice do veículo
        folium.PolyLine(locations=[list(reversed(coords)) for coords in ors.convert.decode_polyline(veiculo['geometry'])['coordinates']], color=color).add_to(mapa)


def otimizar_rota(jobs, vehicles):
    """Recebe a API, os Jobs e os Vehicles e retorna o json da otimização"""
    base_url = 'https://api.openrouteservice.org/optimization'
    headers = {
        'Authorization': f'Bearer {os.environ["OPENROUTE_API_KEY"]}',
        'Content-Type': 'application/json'
    }
    data = {
        "jobs": jobs,
        "vehicles": list(vehicles),
        "options": {
            "g": True  # Solicita a inclusão da geometria
        }
    }
    response = requests.post(base_url, json=data, headers=headers)
    if response.status_code == 200:
        response = response.json()

        arquivo = 'roteiriza/templates/mapas/arquivo.pkl'
        dados_car = carregar_dados(arquivo)
        for rota in response['routes']:
            linha = {rota['vehicle']: [rota['distance'], [item['job'] for item in rota['steps'] if item['type'] == 'job']]}
            dados_car.update(linha)

        with open(arquivo, 'wb') as arquivo:
            pickle.dump(dados_car, arquivo)

    else:
        print('Erro: {}'.format(response))
    return response


def roteirizar(config, dados_vei):
    """Recebe:
    coord_g: Coordenadas dos objetos grandes
    coord_p: Coordenadas dos objetos pequenos
    cap_moto: A capacidade de objetos que a moto transporta
    tempo: Tempo em horas para realizar as entregas
    """

    icon_image = 'roteiriza/static/img/marca_base.png'
    shadow_image = 'roteiriza/static/img/sombra_base.png'
    icon = folium.CustomIcon(
        icon_image,
        icon_size=(40, 40),
        icon_anchor=(20, 40),
        shadow_image=shadow_image,
        shadow_size=(44, 44),
        shadow_anchor=(14, 44),
        popup_anchor=(-3, -36),
    )

    # Apaga os mapas
    mapas_dir = 'roteiriza/templates/mapas'
    if os.path.exists(mapas_dir) and os.listdir(mapas_dir):
        shutil.rmtree(mapas_dir)
        os.makedirs(mapas_dir)

    # Hora final dos veiculos
    final = int((8 * 60 + config.tempo_total) * 60)

    # Coordenada da sede:
    sede = [float(config.sede_long), float(config.sede_lat)]

    hoje = datetime.now()

    # Ordenar a lista de veiculos, primeiro as motos
    dados_vei = sorted(dados_vei, key=lambda x: x[1])

    # Separa em lista de 3 em 3 veiculos
    dados_vei = [dados_vei[i:i+3] for i in range(0, len(dados_vei), 3)]

    m_completo = folium.Map(location=list(reversed(sede)), tiles="cartodbpositron", zoom_start=13)

    feitos = set()
    excluir = set()
    for lista_vei in dados_vei:
        dados_ent = {(item.data_recebido, item.tamanho_grande, item.latitude, item.longitude, item.id)
                     for item in Entregas.query.order_by(Entregas.data_recebido.desc()).limit(56+len(feitos))
                     if item.id not in feitos}
        if not dados_ent:
            break

        jobs = [{"id": dado[4], "location": [float(dado[3]), float(dado[2])], "service": (config.tempo_entrega * 60), "amount": [1], 'skills': [2 if dado[1] else 1], 'priority': max(min((hoje-dado[0]).days, 100), 0)} for dado in
                dados_ent]

        vehicles = [{"id": int(veiculo[0]), "profile": "driving-car", "start": list(sede), "end": list(sede),
                     "capacity": [config.cap_carros if veiculo[1] == 'True' else config.cap_moto],
                     "skills": [1, 2] if veiculo[1] is True else [1], "time_window": [28800, final]} for veiculo in lista_vei]

        excluir |= feitos
        jobs = [job for job in jobs if job['id'] not in excluir]
        otimizado = otimizar_rota(jobs, vehicles)

        for veiculo in otimizado['routes']:
            feitos = {parada['id'] for parada in veiculo['steps'][1:-1]}

            # Média location
            avg_long = [float(ponto['location'][0]) for ponto in veiculo['steps'][1:-1]]
            avg_lat = [float(ponto['location'][1]) for ponto in veiculo['steps'][1:-1]]

            avg_long = (max(avg_long) + min(avg_long)) / 2
            avg_lat = (max(avg_lat) + min(avg_lat)) / 2

            # Criar um novo mapa para o veículo atual
            mapa_veiculo = folium.Map(location=[avg_lat, avg_long], tiles="cartodbpositron", zoom_start=13)

            # Adicionar marcador vermelho
            folium.Marker(location=list(reversed(sede)), icon=icon, popup=(folium.Popup(str('Base'), parse_html=True))).add_to(mapa_veiculo)

            # Adicionar marcadores e polilinhas ao mapa do veículo atual
            add_markers_and_polylines(mapa_veiculo, [veiculo])

            # Salvar o mapa para o veículo atual
            mapa_veiculo.save(f'roteiriza/templates/mapas/mapa_{veiculo["vehicle"]}.html')

        folium.Marker(location=list(reversed(sede)), icon=folium.Icon(color="red")).add_to(m_completo)
        add_markers_and_polylines(m_completo, otimizado['routes'], completo=True)

    m_completo.save('roteiriza/templates/mapas/mapa_completo.html')
