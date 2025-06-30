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
    con = sqlite3.connect("busquedas.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS busquedas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chatid TEXT,
            sku TEXT,
            preciomin REAL
        )
    """)
    con.commit()

asyncio.run(bot.set_my_commands([
    BotCommand('start', text('es','start')),
],language_code='es'))
asyncio.run(bot.set_my_commands([
    BotCommand('start', text('en','start')),
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
    skus=buscar_sku(cadbusqueda)
    if skus is None:
        await bot.reply_to(message, text(message.from_user.language_code,'no_results'))
        return
    # print(skus)
    keyboard = types.InlineKeyboardMarkup()
    for sku,result in skus.items():
        texto= f"{result[0]} - {result[1]} {stores[result[2]]['flag']}"
        callback_data = f"/sku {sku} {result[2]}"
        keyboard.add(types.InlineKeyboardButton(text=texto, callback_data=callback_data))
    await bot.send_message(message.chat.id, text="Resultados encontrados:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda message: True)
async def callbacks(call):
    if call.data.startswith('/sku '):
        parts = call.data.split()
        if len(parts) == 3:
            sku = parts[1]
            # tienda = parts[2]
            # print(f"SKU: {sku}, Tienda: {tienda}")
            await retorna_info(call.message, sku)
            return
        else:
            await bot.answer_callback_query(call.id, "Formato de comando incorrecto.")

if __name__ == "__main__":
    update_cambios()
    inicializa_basedatos()
    asyncio.run(main())
