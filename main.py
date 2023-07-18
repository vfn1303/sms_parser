from fastapi import FastAPI
from pydantic import BaseModel
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor, exceptions
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.dispatcher.filters import Text
import pandas as pd
from dotenv import load_dotenv
import csv, os, re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()

try:
    WEBHOOK_HOST = os.getenv('RAILWAY_STATIC_URL')
    #WEBAPP_HOST = os.getenv('WEBAPP_HOST')
    #WEBAPP_PORT = os.getenv('PORT')
    bot = Bot(token=os.getenv('TOKEN'))
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH') + os.getenv('TOKEN')
    WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH 
    print(WEBHOOK_URL)
    print(WEBHOOK_PATH)
except TypeError:
    exit('Create .env')
dp = Dispatcher(bot)

app = FastAPI()


async def ping():
    await bot.send_message(369701464,"test")

@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
    trigger = CronTrigger(
        year="*", month="*", day="*", hour="0", minute="0", second="1"
    )
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(ping, trigger=trigger)
    scheduler.start()    


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    #await bot.close()


class Msg(BaseModel):
    subject: str
    message: str

@app.post("/sms")
async def demo_post(inp: Msg):
    print(inp)
    try:
        message = inp.message
        start_row = re.findall(r'\[.*?\]', message) #[Александр Д] 
        end_row = re.findall(r'\(.*?\)', message) #(Входящее - 900 )f
        message = re.findall(r'\].*?\(', message) #
        data = message[0][2:len(message)-2].split()
        data.insert(0,start_row[0])
        data.append(end_row[0])
        #data.append(now.strftime('%d/%m/%Y'))
        if 'зачисление' in data:
            data.remove('зачисление')
        elif 'Перевод' in data:
            data.remove('Перевод')
            data.remove('от')
        with open('table.csv', 'a', newline='') as tbl:
            writer = csv.writer(tbl)
            writer.writerow(data)
            print(data)
        return {"error_code": 0}
    except:
        print('Cant parse message')
        return {"error_code": 1}




""" #bot
acl = (1547884469, 369701464,)
admin_only = lambda message: message.from_user.id not in acl

@dp.message_handler(admin_only, content_types=['any'])
async def handle_unwanted_users(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    return


start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.row('Выгрузить все', 'Получить ссылку для приложения')

@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    await message.reply_sticker('CAACAgIAAxkBAAEJty5ktRBJ7cp5zxIthBT1J53_JrG5AwACDg0AAlH5kEqZ_8tFy0kTLC8E', reply_markup=start_kb)   


@dp.message_handler(Text(equals=['Выгрузить все'], ignore_case=True))
async def nav_cal_handler(message: Message):
    #read_file = pd.read_csv('table.csv',delimiter=',')
    with open('table.csv', 'a', newline='') as tbl:
        writer = csv.writer(tbl)
        writer.writerow(['fin','row'])
    #    print(tbl)
    #TODO check if older exists
    #read_file.to_excel('table.xlsx', index=None, header=False)
    await message.answer_document(open("table.csv", "rb"))

@dp.message_handler(Text(equals=['Получить ссылку для приложения'], ignore_case=True))
async def url_cal_handler(message: Message):
    await message.answer(f"Ваша ссылка:\n`{WEBHOOK_HOST}/sms`",parse_mode='Markdown') """
