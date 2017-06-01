from transitions.extensions import GraphMachine

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )
        self.topic = 'null'
        self.num = 0
        self.imgid=''
    
    def is_going_to_getimage(self, update):
        text = update.message.text
        return text.lower() == 'guide dog'
    def is_going_to_image_verify(self, update):
        text = update.message.text
        return text.lower() == 'yes' or text.lower() == 'no'
    def on_enter_image_verify(self, update):
        text = update.message.text
        if text.lower()=='yes':
            update.message.reply_text('Okay, thanks')
            self.go_back(update)
        else:
            update.message.reply_text('Please tell me what you see, or what else did you see?')
            #self.advance(update)
    def on_enter_image_end(self, update):
        text = update.message.text
        if text.lower()!='':
            self.go_back(update)


    def is_going_to_news(self, update):
        text = update.message.text
        return text.lower() == 'instant news' 
    def is_going_to_state1(self, update):
        text = update.message.text
        self.topic = 'w'
        return text.lower() == 'world'

    def is_going_to_state2(self, update):
        text = update.message.text
        self.topic = 's'
        return text.lower() == 'sports'
    def is_going_to_state3(self, update):
        text = update.message.text
        self.topic = 'e'
        return text.lower() == 'entertainment'
    def is_going_to_search(self, update):
        text = update.message.text
        return text.lower() == 'search'

    def is_going_to_lang_sel_EN(self, update):
        text = update.message.text
        self.lang = 'us'
        return text.lower() == 'english'
    def is_going_to_lang_sel_TW(self, update):
        text = update.message.text
        self.lang = 'tw'
        return text.lower() == 'chinese'
    def is_going_to_numOfPost(self, update):
        text = update.message.text
        #num = 0
        try:
            self.num = int(text)
            
            return True
        except ValueError:
            return False
    def is_going_to_fortune(self, update):
        text = update.message.text
        return text.lower() == 'inspire my day'
    def is_going_to_fortune_lang(self, update):
        text = update.message.text
        if text.lower()=='english':
            self.lang='en'
        else:
            self.lang='tw'

        return text.lower() == 'english' or text.lower() == 'chinese'

    def is_going_to_fortune_ACC(self, update):
        text = update.message.text
        return text.lower() == 'yes' or text.lower() == 'no'
    def on_enter_fortune_ACC(self, update):
        text = update.message.text
        if text.lower()=='yes':
            self.go_back(update)
        else:
            self.loop_back(update)

    def on_enter_user(self, update):
        user_name = update.message.chat.first_name +' '+ update.message.chat.last_name
        text = "Hi! " + user_name +" I'm bot!!\nWhat  would you like to see?"

        reply_keyboard = [['Instant News'], ['Image Talks'], ['Fortune']]
        #update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    def on_enter_state1(self, update):
        self.query = False
        update.message.reply_text("World news Selected")
        #handle_language(update)
        #reply_keyboard = [['English', 'Chinese']]
        #text = 'What language would you prefer?'
        #update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        #self.go_back(update)

    def on_enter_state2(self, update):
        self.query = False
        update.message.reply_text("Sports selected")
        #handle_language(update)
        #self.go_back(update)

    def on_enter_state3(self, update):
        self.query = False
        update.message.reply_text("Entertainment Selected")
        #handle_language(update)
        #self.go_back(update)
    def on_enter_search_key(self, update):
        self.query = True
        self.topic = update.message.text

    def on_enter_news_end(self, update):
        self.go_back(update)
        
        
    def on_exit_state1(self, update):
        print('Leaving state1')
    def on_exit_state2(self, update):
        print('Leaving state2')
    def on_exit_state3(self, update):
        print('Leaving state3')
    

    def handle_language(self, update):
        reply_keyboard = [['English', 'Chinese']]
        text = 'What language would you prefer?'
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


