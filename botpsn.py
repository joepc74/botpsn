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

def update_cambios():
    global cambios
    # Actualiza el diccionario de cambios de divisas
    # Si falla, deja el valor anterior
    try:
        cambios=requests.get('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json').json()['eur']
        print(f'Currency changes updated.')
    except Exception as e:
        print(f'Error updating currency changes: {e}')



def inicializa_basedatos():
    global con
    con = sqlite3.connect("botpsn.db")
    con.row_factory = sqlite3.Row

asyncio.run(bot.set_my_commands([
    BotCommand('start', text('es','start')),
    BotCommand('mitienda', text('es','mystore')),
],language_code='es'))
asyncio.run(bot.set_my_commands([
    BotCommand('start', text('en','start')),
    BotCommand('mystore', text('en','mystore')),
]))

async def main():
    try:
        bot.add_custom_filter(asyncio_filters.StateFilter(bot))
        L = await asyncio.gather(
            # tareas_diarias(),
            # tareas_horarias(),
            # borrado_regalos(),
            bot.polling(non_stop=True)
            )
    finally:
        bot.close()


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
# Funcion que devuelve el info de un sku
###########################################################
async def retorna_info(message,sku):
    await bot.send_chat_action(message.chat.id, 'typing')
    info = get_game_info(sku, cambios)
    # print(info)
    if info is None:
        await bot.reply_to(message, "No se encontró información para este SKU.")
    else:
        titulo, precios, tienda = info
        mensaje= f"<b>{titulo}</b>\n"
        for precio, store in precios:
            if tienda==store:
                mensaje+=f"<b>Precio más barato en {stores[store]['name']} {stores[store]['flag']}</b>: {precio:.2f} € <a href='{url_product(sku,store)}'>🏪🏪🏪</a>\n"
            else:
                mensaje+=f"Precio en {stores[store]['name']} {stores[store]['flag']} : {precio:.2f} €\n"
        # print(mensaje)
        await bot.send_message(message.chat.id, mensaje, parse_mode='HTML')

###########################################################
# Resto comandos
###########################################################
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if re.match(r'.*-.*-.*',message.text)!=None:
        await retorna_info(message,message.text)
        return
    # print(message.chat.id)
    # print(message.text)
    await bot.send_chat_action(message.chat.id, 'typing')
    cadbusqueda=message.text.lower().split()
    global con
    cursor = con.cursor()
    cursor.execute("SELECT storedefault FROM usuarios WHERE chatid=?;", (message.from_user.id,))
    row = cursor.fetchone()
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
    if call.data.startswith('/sku '):
        # Callback para buscar un SKU
        # El formato del callback_data es: /sku SKU TIENDA
        parts = call.data.split()
        if len(parts) == 3:
            sku = parts[1]
            # tienda = parts[2]
            # print(f"SKU: {sku}, Tienda: {tienda}")
            await retorna_info(call.message, sku)
            return
        else:
            await bot.answer_callback_query(call.id, text(call.from_user.language_code,'commandincorrect'))
    elif call.data.startswith('/selectstore '):
        # Callback para seleccionar una tienda
        # El formato del callback_data es: /selectstore TIENDA
        parts = call.data.split()
        if len(parts) == 2:
            store = parts[1]
            if store in stores:
                global con
                cursor = con.cursor()
                # print(f"Seleccionando tienda: {store} para el usuario {call.from_user.id}")
                cursor.execute("INSERT INTO usuarios(chatid,storedefault) VALUES ('{chatid}','{store}') ON CONFLICT (chatid) DO UPDATE SET storedefault='{store}' WHERE chatid='{chatid}';".format(chatid=call.from_user.id,store=store))
                con.commit()
                await bot.send_message(call.message.chat.id, text(call.from_user.language_code,'selectedstore')+f" {stores[store]['name']} {stores[store]['flag']}")
            else:
                await bot.answer_callback_query(call.id, text(call.from_user.language_code,'invalidstore'))
        else:
            await bot.answer_callback_query(call.id, text(call.from_user.language_code,'commandincorrect'))

if __name__ == "__main__":
    update_cambios()
    inicializa_basedatos()
    asyncio.run(main())
