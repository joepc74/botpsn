from bs4 import BeautifulSoup
import requests, re, locale
from stores import stores

cambios=requests.get('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json').json()['eur']

def get_game_info(sku):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    titulo=None
    tiendamasbarata=None
    preciomasbarato=float("inf")

    for store in stores:
        url = f'https://store.playstation.com/{store[1]}/product/{sku}'
        # print(f'Fetching {url} for {store[0]}')

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.content, 'html.parser')

        ficha = soup.find('div', class_='psw-pdp-card-anchor')
        if ficha is None:
            print(f'No product found for {sku} in {store[0]} -> {url}')
            continue

        titulo=ficha.find('h1').text.strip()
        # print(f'Title: {titulo} Store: {store[0]}')
        title_elements = ficha.find_all('span', class_='psw-t-title-m')
        print(title_elements)
        for title_element in title_elements:
            texto=title_element.text.strip()
            if texto in ['Game Trial','Prueba de juego']:
                continue
            print(f'Title: {titulo} Store: {store[0]} -> {texto}')
            preciore=re.search(store[3], texto)
            if preciore is None:
                continue
            locale.setlocale(locale.LC_ALL, store[4])
            preciol=locale.atof(preciore.group(1))
            precio=preciol
            if (store[2] is not None):
                precio = preciol / cambios[store[2]]
            if(precio < preciomasbarato):
                preciomasbarato = precio
                tiendamasbarata = store[0]
            print(f'Price of {titulo}: {texto} ({store[2]}) -> {precio:.2f} €')
    if titulo!= None:
        print(f'Cheapest price of {titulo}: {preciomasbarato:.2f} in {tiendamasbarata}')


if __name__ == "__main__":
    get_game_info('EP9000-PPSA08338_00-MARVELSPIDERMAN2')
    get_game_info('EP9000-PPSA21567_00-0000000000000000')
    get_game_info('EP4497-PPSA04029_00-EXPANSION1B00000')
    get_game_info('EP4497-PPSA04027_00-EXPANSION1B00000')
