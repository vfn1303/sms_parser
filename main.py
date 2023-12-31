from fastapi import FastAPI
from pydantic import BaseModel
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv
import csv, os, re, glob
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from urllib.parse import urlencode
from xlsxwriter.workbook import Workbook

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

acl = (1547884469, 369701464)

async def send_csv():
    #await bot.send_sticker('CAACAgIAAxkBAAEJty5ktRBJ7cp5zxIthBT1J53_JrG5AwACDg0AAlH5kEqZ_8tFy0kTLC8E')
    workbook = Workbook('table.xlsx')
    for csvfile in glob.glob(os.path.join('.', '*.csv')):
        with open(csvfile, 'rt', encoding='utf8') as f:
            worksheet = workbook.add_worksheet(csvfile[2:-4] + 'Sheet') 
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
    workbook.close()
    for id in acl:
        #await bot.send_document(id,open("table.csv", "rb"))
        
        await bot.send_document(id,open("table.xlsx", "rb")) 
    open('table.xlsx', 'w').close()
    open('table.csv', 'w').close()
    open('table2.xlsx', 'w').close()
    

@app.on_event("startup")
async def on_startup():
    now = datetime.now()
    print(now.strftime("%H:%M:%S"))
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    trigger = CronTrigger(
        year="*", month="*", day="*", hour="21", minute="1", second="1"
    )
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_csv, trigger=trigger)
    scheduler.start()    
    for id in acl:
        try:
            await bot.send_message(id,'Бот включен!')
        except:
            print('adm not started bot')


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    try:
        for id in acl:
            await bot.send_message(id, "Бот выключен!")
    except:
        print('amd not started bot')
    #await bot.delete_webhook(drop_pending_updates=True)
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
        #data.append(end_row[0])
        #data.append(now.strftime('%d/%m/%Y'))
        if "подозрительный перевод" in str(data):
            with open('table2.csv', 'a', newline='') as tbl:
                writer = csv.writer(tbl)
                writer.writerow(data)
                print(data)
            data.clear()
            return {"error_code": 0}
        if "СЧЁТ" in str(data):
            with open('table2.csv', 'a', newline='') as tbl:
                writer = csv.writer(tbl)
                writer.writerow(data)
                print(data)
            data.clear()
            return {"error_code": 0}
        elif 'зачисление' in data:
            data.remove('зачисление')
            name = data[3:data.index('Баланс:')+1]
            name = ' '.join(name[1:-1])
            del(data[4:data.index('Баланс:')+1])
            data[3]=data[3][:-1]
            data[4]=data[4][:-1]
            data.insert(4,name)
            with open('table.csv', 'a', newline='') as tbl:
                writer = csv.writer(tbl)
                writer.writerow(data)
                print(data)
            data.clear()
            return {"error_code": 0}
        elif 'Перевод' in data:
            data.remove('Перевод')
            name = data[data.index('от'):data.index('Баланс:')+1]
            name = ' '.join(name[1:-1])
            del(data[data.index('от'):data.index('Баланс:')+1])
            data[3]=data[3][:-1]
            data[4]=data[4][:-1]
            data.insert(4,name)
            with open('table.csv', 'a', newline='') as tbl:
                writer = csv.writer(tbl)
                writer.writerow(data)
                print(data)
            data.clear()
            return {"error_code": 0}
        with open('table2.csv', 'a', newline='') as tbl:
            writer = csv.writer(tbl)
            writer.writerow(data)
            print(data)
        return {"error_code": 0}
    except:
        print('Cant parse message')
        return {"error_code": 1}



@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    if message.from_user.id in acl:
        await bot.send_sticker(message.from_user.id,'CAACAgIAAxkBAAEJum1ktmegUWrXDXVBsZp-uzbJioZyNgACfQwAAsoPQEpP5RyRY3qVai8E')
        await bot.send_message(message.from_user.id,f"Ваша ссылка:\n`https://{WEBHOOK_HOST}/sms`",parse_mode='Markdown')


@dp.message_handler(commands=['table'])
async def send_table(message: Message):
    try:
        if message.from_user.id in acl:
            #await bot.send_document(message.from_user.id,open("table.csv", "rb")) 
            #await bot.send_document(message.from_user.id,open("table2.csv", "rb")) 

            workbook = Workbook('table.xlsx')

            for csvfile in glob.glob(os.path.join('.', '*.csv')):
                with open(csvfile, 'rt', encoding='utf8') as f:
                    worksheet = workbook.add_worksheet(csvfile[2:-4] + 'Sheet')
                    reader = csv.reader(f)
                    for r, row in enumerate(reader):
                        for c, col in enumerate(row):
                            worksheet.write(r, c, col)
            workbook.close()
            await bot.send_document(message.from_user.id,open("table.xlsx", "rb")) 
    except Exception as e: print(e)

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
