from config import *

textos={
    'es':{
        'start':"Hola.\nBienvenido al mayor bot de busquedas de mejores precios en psn.",
        'mystore':"Selecciona la tienda donde realizar las busquedas.",
        'mytrackings':"Lista los seguimientos que tienes activos.",
        'no_results':"No se han encontrado resultados para tu busqueda.",
        'selectedstore':"Has seleccionado la tienda: ",
        'commandincorrect':"Formato de comando incorrecto.",
        'invalidstore':"Tienda no válida. Por favor, selecciona una tienda válida.",
        'resultsfound':"Resultados encontrados:",
        'prizecheap':"<b>Precio más barato en {store} {flag}</b>: {precio:.2f} € <a href='{url}'>🏪🏪🏪</a>\n",
        'prizenocheap':"Precio en {store} {flag} : {precio:.2f} €\n",
        'no_trackings':"No tienes seguimientos activos.",
        'mytrackingstores':"Selecciona las tiendas donde quieres realizar los seguimientos.",
        'newcheatprize':"Nuevo precio más barato en {store} {flag}: {precio:.2f} € <a href='{url}'>🏪🏪🏪</a>",
        'nosearchstore':"No has seleccionado ninguna tienda para realizar la busqueda, usando Spain por defecto, usa /mitienda para especificar tu tienda de busquedas.",
        'mytracksline':"Titulo: {titulo} - Precio mínimo: {precio:.2f} € - /untrack_{id}\n",
        'untrackedsuccess':"Seguimiento eliminado correctamente.",
        'searching':"Buscando precios...",
    },
    'en':{
        'start':"Hello.\nWelcome to the biggest search bot for the best prices on PSN.",
        'mystore':"Select the store where you want to search.",
        'mytrackings':"List your active trackings.",
        'no_results':"No results found for your search.",
        'selectedstore':"You have selected the store: ",
        'commandincorrect':"Incorrect command format.",
        'invalidstore':"Invalid store. Please select a valid store.",
        'resultsfound':"Results found:",
        'prizecheap':"<b>Cheapest price in {store} {flag}</b>: {precio:.2f} € <a href='{url}'>🏪🏪🏪</a>\n",
        'prizenocheap':"Price in {store} {flag} : {precio:.2f} €\n",
        'no_trackings':"You have no active trackings.",
        'mytrackingstores':"Select the stores where you want to track prices.",
        'newcheatprize':"New cheapest price in {store} {flag}: {precio:.2f} € <a href='{url}'>🏪🏪🏪</a>",
        'nosearchstore':"You have not selected any store for searching, using Spain by default, use /mystore to specify your search store.",
        'mytracksline':"Title: {titulo} - Minimum price: {precio:.2f} € - /untrack_{id}\n",
        'untrackedsuccess':"Tracking successfully removed.",
        'searching':"Searching for prices...",
    },
}

def text(idioma,texto):
    try:
        return textos[idioma][texto]
    except:
        return textos['en'][texto]