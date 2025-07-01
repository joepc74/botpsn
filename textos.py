from config import *

textos={
    'es':{
        'start':"Hola.\nBienvenido al mayor bot de busquedas de mejores precios en psn.",
        'mystore':"Selecciona la tienda donde realizar las busquedas.",
        'no_results':"No se han encontrado resultados para tu busqueda.",
        'selectedstore':"Has seleccionado la tienda: ",
    },
    'en':{
        'start':"Hello.\nWelcome to the biggest search bot for the best prices on PSN.",
        'mystore':"Select the store where you want to search.",
        'no_results':"No results found for your search.",
        'selectedstore':"You have selected the store: ",
    },
}

def text(idioma,texto):
    try:
        return textos[idioma][texto]
    except:
        return textos['en'][texto]