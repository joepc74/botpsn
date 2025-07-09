# /bin/python3

import requests
from stores import *
import sqlite3
from telebot import asyncio_filters, types
from telebot.types import *
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
import asyncio
from textos import *


con=None
from config import TELEGRAM_TOKEN
bot = AsyncTeleBot(TELEGRAM_TOKEN)
cambios=None

def inicializa_basedatos():
    global con
    con = sqlite3.connect("botpsn.db")
    con.row_factory = sqlite3.Row

asyncio.run(bot.set_my_commands([
    BotCommand('start', text('es','start')),
    BotCommand('mitienda', text('es','mystore')),
    BotCommand('misseguimientos', text('es','mytrackings')),
    BotCommand('mistiendastracking', text('es','mytrackingstores')),
],language_code='es'))
asyncio.run(bot.set_my_commands([
    BotCommand('start', text('en','start')),
    BotCommand('mystore', text('en','mystore')),
    BotCommand('mytrackings', text('en','mytrackings')),
    BotCommand('mytrackingstores', text('es','mytrackingstores')),
]))

async def main():
    try:
        bot.add_custom_filter(asyncio_filters.StateFilter(bot))
        L = await asyncio.gather(
            update_cambios(),
            actualiza_trackings(),
            bot.polling(non_stop=True)
            )
    finally:
        bot.close()

async def update_cambios():
    global cambios
    while True:
        # Actualiza el diccionario de cambios de divisas
        # Si falla, deja el valor anterior
        try:
            cambios=requests.get('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json').json()['eur']
            print(f'Currency changes updated.')
        except Exception as e:
            print(f'Error updating currency changes: {e}')
        await asyncio.sleep(12*60*60) # se ejecuta cada 12 horas

###########################################################
# Tarea de actualizacion de trackings
###########################################################
async def actualiza_trackings():
    global con
    cursor= con.cursor()
    while True:
        print("Checking for price updates...")
        seguimentos= cursor.execute("SELECT chatid,sku,preciomin,lang FROM trackings;").fetchall()
        if seguimentos:
            for seguimiento in seguimentos:
                chatid, sku, preciomin,lang = seguimiento
                # obtiene las tiendas seleccionadas por el usuario
                info = await get_game_info(sku, cambios, con)
                if info is None:
                    continue
                titulo, precios, tienda, precio_actual = info
                # si el precio actual es menor que el precio mínimo registrado, envía un mensaje al usuario
                if precio_actual < preciomin:
                    mensaje = f"<b>{titulo}</b>\n"
                    mensaje += text(lang,'newcheatprize').format(store=stores[tienda]['name'], flag=stores[tienda]['flag'], precio=precio_actual, url=url_product(sku, tienda))
                    try:
                        # se envía el mensaje al usuario
                        await bot.send_message(chatid, mensaje, parse_mode='HTML')
                        # se actualiza el precio mínimo en la base de datos
                        cursor.execute("UPDATE trackings SET preciomin=? WHERE chatid=? AND sku=?;", (precio_actual, chatid, sku))
                        con.commit()
                    except Exception as e:
                        print(f"Error sending message to {chatid}: {e}")
        print("Price updates checked.")
        await asyncio.sleep(6*60*60) # se ejecuta cada 6 horas

###########################################################
# Comando start
###########################################################
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, text(message.from_user.language_code,'start'))

###########################################################
# Comando mystore
###########################################################
@bot.message_handler(commands=['mystore','mitienda'])
async def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    for store,data in stores.items():
        texto= f"{data['name']} {data['flag']}"
        callback_data = f"/selectstore {store}"
        keyboard.add(types.InlineKeyboardButton(text=texto, callback_data=callback_data))
    await bot.send_message(message.chat.id, text=text(message.from_user.language_code,'mystore'), reply_markup=keyboard)

###########################################################
# Comando mytrackingstores
###########################################################
def botonera_select_stores(chatid,stores_selected=None):
    CHECK_CHAR = '✅'
    UNCHECK_CHAR = '⬜'
    if stores_selected is None:
        global con
        cursor = con.cursor()
        stores_selected=cursor.execute("SELECT searchstores FROM usuarios WHERE chatid=?;", (chatid,)).fetchone()
        if stores_selected is None or stores_selected['searchstores'] is None:
            stores_selected=set()
        else:
            stores_selected=set(stores_selected['searchstores'].split('#'))
    # print(f"---Selected stores for user {chatid}: {stores_selected}")
    keyboard=[]
    for store,data in stores.items():
        # print(f"---Adding store {store} to keyboard")
        # print(f"---Store selected: {store in stores_selected}")
        keyboard.append([InlineKeyboardButton(
            f"{CHECK_CHAR if store in stores_selected else UNCHECK_CHAR} {data['name']} {data['flag']}",
            callback_data=f"/togglets__{store}"
        )])

    return InlineKeyboardMarkup(keyboard)

@bot.message_handler(commands=['mytrackingstores','mistiendastracking'])
async def select_tracking_stores(message):
    await bot.send_message(message.from_user.id,text(message.from_user.language_code,'mytrackingstores'), reply_markup=botonera_select_stores(message.from_user.id))
    return

###########################################################
# Comando mytrackings
###########################################################
@bot.message_handler(commands=['mytrackings','misseguimientos'])
async def send_mytrackings(message):
    global con
    cursor = con.cursor()
    cursor.execute("SELECT sku,preciomin FROM trackings WHERE chatid=?;", (message.from_user.id,))
    seguimientos = cursor.fetchall()
    lang=message.from_user.language_code
    if not seguimientos:
        await bot.reply_to(message, text(lang,'no_trackings'))
        return
    respuesta=""
    for sku, precio in seguimientos:
        # respuesta += "SKU: {sku} - Titulo: {titulo} - Precio mínimo: {precio:.2f} €\n".format(sku=sku, titulo=get_game_title(sku,con), precio=precio)
        respuesta += text(lang,'mytracksline').format(sku=sku, titulo=get_game_title(sku,con), precio=precio)
    await bot.reply_to(message, respuesta, parse_mode='HTML')
    # await bot.delete_message(message.chat.id, message.id)  # Elimina el mensaje original para evitar spam

###########################################################
# Funcion que devuelve el info de un sku
###########################################################
async def retorna_info(message,sku, lang='es'):
    await bot.send_chat_action(message.chat.id, 'typing')
    info = await get_game_info(sku, cambios,con)
    if info is None:
        await bot.reply_to(message, "No se encontró información para este SKU.")
    else:
        titulo, precios, tienda, preciomasbarato = info
        mensaje=f"<b>{titulo}</b>\n"
        for precio, store in precios:
            if tienda==store:
                mensaje+=text(lang,'prizecheap').format(store=stores[store]['name'], flag=stores[store]['flag'], precio=precio, url=url_product(sku,store))
            else:
                mensaje+=text(lang,'prizenocheap').format(store=stores[store]['name'], flag=stores[store]['flag'], precio=precio)
        # print(mensaje)
        await bot.send_message(message.chat.id, mensaje, parse_mode='HTML', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Track", callback_data=f"/track {sku} {precio}"))),

###########################################################
# Resto comandos
###########################################################
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if re.match(r'.*-.*-.*',message.text)!=None:
        await retorna_info(message,message.text, message.from_user.language_code)
        return
    # print(message.chat.id)
    # print(message.text)
    await bot.send_chat_action(message.chat.id, 'typing')
    cadbusqueda=message.text.lower().split()
    global con
    cursor = con.cursor()
    cursor.execute("SELECT storedefault FROM usuarios WHERE chatid=?;", (message.from_user.id,))
    row = cursor.fetchone()
    if row is None or row[0] is None:
        # Si no hay tienda por defecto, se usa España
        await bot.reply_to(message, text(message.from_user.language_code,'nosearchstore'))
        row = ['ESP']
    skus=buscar_sku(cadbusqueda, 'ESP' if row is None else row[0])
    if skus is None:
        await bot.reply_to(message, text(message.from_user.language_code,'no_results'))
        return
    # print(skus)
    keyboard = types.InlineKeyboardMarkup()
    for sku,result in skus.items():
        texto= f"{result[0]} - {result[1]} {stores[result[2]]['flag']}"
        callback_data = f"/sku {sku} {result[2]}"
        keyboard.add(types.InlineKeyboardButton(text=texto, callback_data=callback_data))
    await bot.send_message(message.chat.id, text=text(message.from_user.language_code,'resultsfound'), reply_markup=keyboard)

###########################################################
# Callbacks para los botones de resultados
# Se ejecuta cuando el usuario pulsa un botón de resultado
###########################################################
@bot.callback_query_handler(func=lambda message: True)
async def callbacks(call):
    lang=call.from_user.language_code
    userid=call.from_user.id
    if call.data.startswith('/sku '):
        # Callback para buscar un SKU
        # El formato del callback_data es: /sku SKU TIENDA
        parts = call.data.split()
        if len(parts) == 3:
            sku = parts[1]
            # tienda = parts[2]
            # print(f"SKU: {sku}, Tienda: {tienda}")
            await retorna_info(call.message, sku, lang)
            return
        else:
            await bot.answer_callback_query(call.id, text(lang,'commandincorrect'))
    elif call.data.startswith('/selectstore '):
        # Callback para seleccionar una tienda
        # El formato del callback_data es: /selectstore TIENDA
        parts = call.data.split()
        if len(parts) == 2:
            store = parts[1]
            if store in stores:
                global con
                cursor = con.cursor()
                # print(f"Seleccionando tienda: {store} para el usuario {userid}")
                cursor.execute("INSERT INTO usuarios(chatid,storedefault) VALUES ('{chatid}','{store}') ON CONFLICT (chatid) DO UPDATE SET storedefault='{store}' WHERE chatid='{chatid}';".format(chatid=userid,store=store))
                con.commit()
                await bot.send_message(call.message.chat.id, text(lang,'selectedstore')+f" {stores[store]['name']} {stores[store]['flag']}")
                await bot.delete_message(call.message.chat.id, call.message.id)  # Elimina el mensaje original para evitar spam
            else:
                await bot.answer_callback_query(call.id, text(lang,'invalidstore'))
        else:
            await bot.answer_callback_query(call.id, text(lang,'commandincorrect'))
    elif call.data.startswith('/track '):
        # Callback para trackear un SKU
        # El formato del callback_data es: /track SKU
        parts = call.data.split()
        if len(parts) == 3:
            sku = parts[1]
            precio=parts[2]
            cursor = con.cursor()
            cursor.execute("INSERT INTO trackings(chatid,sku,preciomin,lang) SELECT '{chatid}','{sku}','{precio}','{lang}' WHERE NOT EXISTS(SELECT chatid,sku FROM trackings WHERE chatid = '{chatid}' AND sku = '{sku}');".format(chatid=userid, sku=sku,precio=precio,lang=lang))
            con.commit()
            await bot.answer_callback_query(call.id, "SKU añadido a seguimiento.")
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id,message_id=call.message.id, reply_markup=None)
        else:
            await bot.answer_callback_query(call.id, text(lang,'commandincorrect'))
    elif call.data.startswith('/togglets__'):
        # Callback para alternar la selección de una tienda en la lista de seguimiento
        # El formato del callback_data es: /togglets__TIENDA
        parts = call.data.split('__')
        if len(parts) == 2:
            store = parts[1]
            cursor = con.cursor()
            cursor.execute("SELECT searchstores FROM usuarios WHERE chatid=?;", (userid,))
            row = cursor.fetchone()
            if row is None or row[0] is None:
                stores_selected = set()
            else:
                stores_selected = set(row[0].split('#'))
            # print(f"Toggling store: {store} for user {userid}")
            # print(f"Current selected stores: {stores_selected}")
            if store in stores_selected:
                stores_selected.remove(store)
            else:
                stores_selected.add(store)
            cursor.execute("INSERT INTO usuarios(chatid,searchstores) VALUES ('{chatid}','{stores}') ON CONFLICT (chatid) DO UPDATE SET searchstores='{stores}' WHERE chatid='{chatid}';".format(chatid=userid,stores='#'.join(stores_selected)))
            con.commit()
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=text(lang,'mytrackingstores'), reply_markup=botonera_select_stores(userid,stores_selected))
        else:
            await bot.answer_callback_query(call.id, text(lang,'commandincorrect'))

if __name__ == "__main__":
    inicializa_basedatos()
    asyncio.run(main())
