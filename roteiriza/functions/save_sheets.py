import openpyxl
from sqlalchemy import text
from roteiriza import database
from roteiriza.models import Entregas
from roteiriza.functions.end_to_coord import coordenadas


def adic_planilha():
    # Abrindo o arquivo Excel
    wb = openpyxl.load_workbook("roteiriza/static/files/planilha.xlsx")
    ws = wb.active

    entregas_data = []
    # Iterando pelas linhas da planilha
    for row in ws.iter_rows(min_row=2, values_only=True):  # Ignorando a primeira linha de cabeçalho
        end_completo = f'{row[4]} - {row[5]}, Teresina, Piauí'
        coord = coordenadas(end_completo)
        grande = True if row[3] == 'SIM' else False
        entrega = {
            'data_recebido': row[0].date(),
            'descricao': row[1],
            'telefone': row[2],
            'tamanho_grande': grande,
            'endereco': row[4],
            'bairro': row[5],
            'latitude': coord['lat'],
            'longitude': coord['lng']
        }
        entregas_data.append(entrega)

    # Inserindo os dados no banco de dados em lote
    sql = """
    INSERT INTO entregas (data_recebido, descricao, telefone, tamanho_grande, endereco, bairro, latitude, longitude) 
    VALUES (:data_recebido, :descricao, :telefone, :tamanho_grande, :endereco, :bairro, :latitude, :longitude)
    """
    database.session.execute(text(sql), entregas_data)
    database.session.commit()
