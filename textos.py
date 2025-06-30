from config import *

textos={
    'es':{
        'start':"Hola.\nBienvenido al mayor bot de busquedas de mejores precios en psn.",
        'no_results':"No se han encontrado resultados para tu busqueda.",
    },
    'en':{
        'start':"Hello.\nWelcome to the biggest search bot for the best prices on PSN.",
        'no_results':"No results found for your search.",
    },
}

def text(idioma,texto):
    try:
        return textos[idioma][texto]
    except:
        return textos['en'][texto]