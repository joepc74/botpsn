from config import *

textos={
    'es':{
        'start':"Hola.\nBienvenido al mayor bot de busquedas de mejores precios en psn.",
        'mystore':"Selecciona la tienda donde realizar las busquedas.",
        'no_results':"No se han encontrado resultados para tu busqueda.",
        'selectedstore':"Has seleccionado la tienda: ",
        'commandincorrect':"Formato de comando incorrecto.",
        'invalidstore':"Tienda no válida. Por favor, selecciona una tienda válida.",
        'resultsfound':"Resultados encontrados:",
        'prizecheap':"<b>Precio más barato en {store} {flag}</b>: {precio:.2f} € <a href='{url}'>🏪🏪🏪</a>\n",
        'prizenocheap':"Precio en {store} {flag} : {precio:.2f} €\n"
    },
    'en':{
        'start':"Hello.\nWelcome to the biggest search bot for the best prices on PSN.",
        'mystore':"Select the store where you want to search.",
        'no_results':"No results found for your search.",
        'selectedstore':"You have selected the store: ",
        'commandincorrect':"Incorrect command format.",
        'invalidstore':"Invalid store. Please select a valid store.",
        'resultsfound':"Results found:",
        'prizecheap':"<b>Cheapest price in {store} {flag}</b>: {precio:.2f} € <a href='{url}'>🏪🏪🏪</a>\n",
        'prizenocheap':"Price in {store} {flag} : {precio:.2f} €\n"
    },
}

def text(idioma,texto):
    try:
        return textos[idioma][texto]
    except:
        return textos['en'][texto]