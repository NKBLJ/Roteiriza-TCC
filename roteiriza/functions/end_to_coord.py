import googlemaps
import os


def coordenadas(endereco):
    gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])
    geocode_result = gmaps.geocode(endereco)

    return geocode_result[0]['geometry']['location']


if __name__ == '__main__':
    endereco = 'Av. Centenário, 2593 - Aeroporto, Teresina, PI'
    print(coordenadas(endereco))
