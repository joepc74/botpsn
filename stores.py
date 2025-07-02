# Listado de currencies en https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json
from bs4 import BeautifulSoup
import requests, re, locale, json, asyncio, time

sem = asyncio.Semaphore()

stores={
    'ESP':{'name':'Spain',     'flag':'🇪🇸', 'psnlocale': 'es-es', 'currency': None , 'regex': r"(\d+\,\d+)\s€",         'coinlocale':'es_ES'},
    'IND':{'name':'India',     'flag':'🇮🇳', 'psnlocale': 'en-in', 'currency': 'inr', 'regex': r"Rs\s(\d+,\d+)",         'coinlocale':'en_IN'},
    'TUR':{'name':'Turkey',    'flag':'🇹🇷', 'psnlocale': 'en-tr', 'currency': 'try', 'regex': r"(\d*\.*\d+,\d+)\sTL",   'coinlocale':'es_ES'},
    'HKG':{'name':'Hong Kong', 'flag':'🇭🇰', 'psnlocale': 'en-hk', 'currency': 'hkd', 'regex': r"HK\$(\d+\.\d+)",        'coinlocale':'en_EN'},
    'USA':{'name':'USA',       'flag':'🇺🇸', 'psnlocale': 'en-us', 'currency': 'usd', 'regex': r"\$(\d+\.\d+)",          'coinlocale':'en_EN'},
}

def buscar_sku(texto,storecode='ESP'):
    resultados={}
    store=stores[storecode]
    url = f'https://store.playstation.com/{store['psnlocale']}/search/{texto}'
    # print(f'Fetching {url} for {store['name']}')

    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    fichas = soup.find('ul', class_='psw-grid-list')
    if fichas is None:
        return None
    for ficha in fichas.find_all('li'):
        enlace=ficha.find('a')
        subtexto=enlace.find('span', class_='psw-product-tile__product-type')
        if subtexto is None or subtexto.text.strip() in ['Game Bundle','Paquete de juego']:
            datos=json.loads(enlace.get('data-telemetry-meta'))
            if datos['price'] in ['No disponible','Unavailable','Gratis','Free']:
                continue
            # print(datos)
            if datos['id'] not in resultados:
                resultados[datos['id']]=[datos['name'],datos['price'],storecode]
                if len(resultados) >= 10:
                    return resultados
    # print(resultados)

    return resultados

def url_product(sku,storecode='ESP'):
    return f'https://store.playstation.com/{stores[storecode]['psnlocale']}/product/{sku}'

async def get_game_info(sku,cambios,con):
    global sem
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    resultados=[]
    titulo=None
    tiendamasbarata=None
    preciomasbarato=float("inf")

    for store,data in stores.items():
        await sem.acquire()
        try:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM busquedas WHERE sku=? AND store=? AND actualizado>?;", (sku,store,int(time.time())-3*60*60))
            rows = cursor.fetchall()
            if rows==[]:
                # print(f'Fetching {sku} for {store}...')
                url = url_product(sku, store)

                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    cursor.execute("INSERT INTO busquedas (sku, store, precio) VALUES (?, ?, ?);", (sku, store, 'null'))
                    con.commit()

                    continue
                soup = BeautifulSoup(response.content, 'html.parser')

                ficha = soup.find('div', class_='psw-pdp-card-anchor')
                if ficha is None:
                    # print(f'No product found for {sku} in {store[0]} -> {url}')
                    cursor.execute("INSERT INTO busquedas (sku, store, precio) VALUES (?, ?, ?);", (sku, store, 'null'))
                    con.commit()
                    continue

                if titulo==None:
                    titulo=ficha.find('h1').text.strip()
                # print(f'Title: {titulo} Store: {data['name']}')
                title_elements = ficha.find_all('label', class_='psw-label')
                # print(title_elements)
                for title_element in title_elements:
                    if title_element.find('span', class_='psw-icon') is not None:
                        cursor.execute("INSERT INTO busquedas (sku, store, precio) VALUES (?, ?, ?);", (sku, store, 'null'))
                        con.commit()
                        continue
                    texto=title_element.find('span',class_='psw-t-title-m').text.strip()
                    if texto in ['Game Trial','Prueba de juego']:
                        continue
                    # print(f'Title: {titulo} Store: {data['name']} -> {texto}')
                    preciore=re.search(data['regex'], texto)
                    if preciore is None:
                        cursor.execute("INSERT INTO busquedas (sku, store, precio) VALUES (?, ?, ?);", (sku, store, 'null'))
                        con.commit()
                        continue
                    locale.setlocale(locale.LC_ALL, data['coinlocale'])
                    preciol=locale.atof(preciore.group(1))
                    precio=preciol
                    if (data['currency'] is not None):
                        precio = preciol / cambios[data['currency']]
                    if(precio < preciomasbarato):
                        preciomasbarato = precio
                        tiendamasbarata = store
                    # print(f'Price of {titulo}: {texto} ({store}) -> {precio:.2f} €')
                    cursor.execute("INSERT INTO busquedas (sku, store, titulo, precio) VALUES (?, ?, ?, ?);", (sku, store, titulo, precio))
                    con.commit()
                    resultados.append([precio, store])
            else:
                for row in rows:
                    precio = row['precio']
                    # print(f'Using cached price for {sku} in {store}: {precio}')
                    if precio==None or precio=='null':
                        continue
                    if(precio < preciomasbarato):
                        preciomasbarato = precio
                        tiendamasbarata = store
                    if titulo is None:
                        titulo=row['titulo']
                    resultados.append([precio, store])
        finally:
            sem.release()
    # if titulo!= None:
    #     print(f'Cheapest price of {titulo}: {preciomasbarato:.2f} in {tiendamasbarata}')
    return [titulo, resultados, tiendamasbarata]


if __name__ == "__main__":
    # buscar_sku('cyberpunk 2077')
    # cambios=requests.get('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json').json()['eur']
    # get_game_info('EP4497-PPSA04029_00-EXPANSION1B00000',cambios)
    # print(get_game_info('EP4497-PPSA04027_00-EXPANSION1B00000',cambios))
    pass