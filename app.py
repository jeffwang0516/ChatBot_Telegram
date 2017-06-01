import sys
from io import BytesIO
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import telegram
from flask import Flask, request, send_file

from fsm import TocMachine
import google_news as news

import boto3
client = boto3.client('rekognition')
from gtts import gTTS

import sqlite3
import random

#cursor = conn.execute("SELECT * from fortunes")
API_TOKEN = '349456127:AAHUnR5v_aVeOBBWARNRK_xMGoss-zWWkZw'
WEBHOOK_URL = 'https://b41041f9.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'news',
        'state1',
        'state2',
        'state3',
        'sel_EN',
        'sel_TW',
        'numOfPosts',
        'news_end',
        'search',
        'search_key',
        'image_mode',
        'image_get',
        'image_verify',
        'image_reply',
        'fortune',
        'fortune_lang',
        'fortune_ACC'

    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'image_mode',
            'conditions': 'is_going_to_getimage'
        },
        {
            'trigger': 'advance',
            'source': 'image_mode',
            'dest': 'image_get',
        },
        {
            'trigger': 'advance',
            'source': 'image_get',
            'dest': 'image_verify',
            'conditions': 'is_going_to_image_verify'
        },
        {
            'trigger': 'advance',
            'source': 'image_verify',
            'dest': 'image_reply'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'news',
            'conditions': 'is_going_to_news'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'state1',
            'conditions': 'is_going_to_state1'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'state2',
            'conditions': 'is_going_to_state2'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'state3',
            'conditions': 'is_going_to_state3'
        },
        {
            'trigger': 'advance',
            'source': 'news',
            'dest': 'search',
            'conditions': 'is_going_to_search'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'fortune',
            'conditions': 'is_going_to_fortune'
        },
        {
            'trigger': 'advance',
            'source': 'fortune',
            'dest': 'fortune_lang',
            'conditions': 'is_going_to_fortune_lang'
        },
        {
            'trigger': 'advance',
            'source': 'fortune_lang',
            'dest': 'fortune_ACC',
            'conditions': 'is_going_to_fortune_ACC'
        },
        {
            'trigger': 'loop_back',
            'source': 'fortune_ACC',
            'dest': 'fortune_lang'
        },

        

        {
            'trigger': 'advance',
            'source': 'search',
            'dest': 'search_key'
            
        },
        {
            'trigger': 'advance',
            'source': [
                'state1',
                'state2',
                'state3'
            ],            
            'dest': 'sel_EN',
            'conditions': 'is_going_to_lang_sel_EN'
        },
        {
            'trigger': 'advance',
            'source': [
                'state1',
                'state2',
                'state3'
                
            ],
            'dest': 'sel_TW',
            'conditions': 'is_going_to_lang_sel_TW'
        },
        {
        
            'trigger': 'advance',
            'source': [
                'sel_EN',
                'sel_TW',
                'search_key'

            ],
            'dest': 'numOfPosts',
            'conditions': 'is_going_to_numOfPost'

        },
        {
            'trigger': 'advance',
            'source': 'numOfPosts',
            'dest': 'news_end'

        },


        {
            'trigger': 'go_back',
            'source': ['news_end', 'fortune_ACC', 'image_verify', 'image_reply'] ,
            'dest': 'user'
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))
'''
conn = sqlite3.connect('bot_db.db')
conn.execute('DROP TABLE STATEREC')
conn.execute('CREATE TABLE STATEREC(ID TEXT PRIMARY KEY, STATE TEXT)')
conn.close()
'''
@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    '''conn = sqlite3.connect('bot_db.db')
    cursor = conn.execute("SELECT STATE from STATEREC WHERE ID=(?)", (str(update.message.chat.id),))
    ori_state=''
    for row in cursor:
        ori_state = row[0]
    #print(ori_state)
    if not ori_state:
        conn.execute("INSERT INTO STATEREC (ID, STATE) VALUES(?,?)", (str(update.message.chat.id),machine.state))
    else:
        if ori_state!=machine.state:
            
            switch_to_state = getattr(machine, 'to_'+str(ori_state))
            switch_to_state()
    '''
    machine.advance(update)
    #print(update.message.chat.id)

    #HANDLE for each state
    handle_reply(update, machine.state)

    '''conn.execute("UPDATE STATEREC SET STATE = ? WHERE ID=?", (machine.state, str(update.message.chat.id)))
    conn.commit()
    conn.close()'''
    return 'ok'
def handle_reply(update, state):
    if state == 'user':
        user_name = update.message.chat.first_name +' '+ update.message.chat.last_name
        text = "Hi! " + user_name +" I'm bot!!\nWhat  would you like to see?"

        reply_keyboard = [['Instant News'], ['Guide Dog'], ['Inspire my day']]
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    elif state == 'news':
        text = "Choose a category~~"
        reply_keyboard = [['World', 'Sports'],[ 'Entertainment','Search']]
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    elif state == 'state1' or state == 'state2'or state == 'state3':
        handle_language(update)
    elif state == 'sel_TW' or state == 'sel_EN':
        update.message.reply_text('How many stories do you want?(numbers)')

    elif state == 'numOfPosts':
        #print(machine.topic+machine.lang+str(machine.num))
        #machine.go_back(update)
        content=[]
        if  not machine.query:
            content = news.get_news(machine.topic, machine.lang, machine.num)
        else:
            content = news.query_news( machine.topic ,machine.num )
        for post in content:
            update.message.reply_text(post)
        update.message.reply_text('Type any words to try other stuffs!')
        machine.advance(update)

    elif state == 'search':
        update.message.reply_text('Enter keywords!!')
        #machine.advance(update)
    elif state == 'search_key':
        update.message.reply_text('How many stories do you want?(numbers)')
        #content = news.query_news( update.message.text )
        #for post in content:
        #    update.message.reply_text(post)

        #machine.go_back(update)

    elif state == 'image_mode':
        update.message.reply_text('HI, I\'m guide dog!\nSent me a photo, plz')
    elif state == 'image_get':
        if not update.message.photo:
            update.message.reply_text('Sent me a photo, plz')
        else:
            
            update.message.reply_text('Please wait~ Almost Done!')
            img_id = update.message.photo[-1].file_id
            machine.imgid=str(update.message.message_id)
            #print(img_id)
            imgfile = bot.get_file(img_id)
            imgfile.download('./photo/'+str(update.message.message_id)+'.jpeg')
            with open('./photo/'+str(update.message.message_id)+'.jpeg', 'rb') as img:
                response = client.detect_labels(Image={'Bytes': img.read()})
            speech=''
            for el in response['Labels']:
                if el['Name'].lower() == 'person':
                    response['Labels'].remove(el)
                    break
            for el in response['Labels']:
                if el['Name'].lower() == 'human' :
                    response['Labels'].remove(el)
                    break

            if len(response['Labels']) > 1:        
                speech = 'I saw '+ response['Labels'][0]['Name']+', or maybe '+ response['Labels'][1]['Name']
                if len(response['Labels']) > 2:
                    speech += ' and '+ response['Labels'][2]['Name']
            else:
                speech = 'I saw nothing'
            
            #print(speech)
            tts = gTTS(text=speech, lang='en', slow=False)

            #f = tempfile.TemporaryFile()
            tts.save('./speech/voice.mp3')
            f = open('./speech/voice.mp3', 'rb')
            bot.send_voice(chat_id=update.message.chat_id, voice=f)
            f.close()
            reply_keyboard = [['YES', 'NO']]
            text = 'Is it familiar with what you saw??'
            update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

            #update.message.reply_text('Type any words to try other stuffs!')
            #machine.go_back(update)
    elif state == 'image_reply':
        reply = update.message.text
        print(reply)
        conn = sqlite3.connect('bot_db.db')
        conn.execute("INSERT INTO imgfeedback (IMGID, FEEDBACK) VALUES (?,?)", (str(machine.imgid),reply))
        conn.commit()
        conn.close()
        update.message.reply_text('Thanks!')
        update.message.reply_text('Type any words to try other stuffs!')
        machine.go_back(update)
    elif state == 'fortune':
        update.message.reply_text("I'll give you some inspirations")
        handle_language(update)
    elif state == 'fortune_lang':
        conn = sqlite3.connect('bot_db.db')
        fortune_str=''
        if machine.lang == 'en':
            cursor = conn.execute("SELECT count(*) from fortunes")
            cnt=0
            for r in cursor:
                cnt=r[0]

            ursor = conn.execute("SELECT * from fortunes WHERE ID = "+str(random.randint(1,cnt)))
            for a in ursor:
                #print(a[0],a[1])
                fortune_str = a[1]
        else:
            cursor = conn.execute("SELECT count(*) from fortunes2")
            cnt=0
            for r in cursor:
                cnt=r[0]

            ursor = conn.execute("SELECT * from fortunes2 WHERE ID = "+str(random.randint(1,cnt)))
            for a in ursor:
                #print(a[0],a[1])
                fortune_str = a[1]

        conn.close()
        update.message.reply_text(fortune_str)

        reply_keyboard = [['YES', 'NO']]
        text = 'Is it good?'
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
        

def handle_language(update):
    reply_keyboard = [['English', 'Chinese']]
    text = 'What language would you prefer?'
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
      


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run(threaded=True)
