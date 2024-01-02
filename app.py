from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import json
from linebot.models import TextSendMessage


#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *
#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
import tempfile, os
import datetime
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi('KbpSLEW/T1ETFs903NTolbNGYhuX4h+nwyQuIA1u9FYoIJvJX53CPJ9p1PizfJvLmBORAe/5P5GC8CarvJhv6N1kMul16scPIG1ahwiq0At4C1bVnpUExpkDil8vaA/J7uZu3Noha7QOyRdtDC3segdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('3650d1fdf0030008e78b4026747858d5')

def fetch_thingspeak_data(field_name):
    try:
        # Modify the ThingSpeak API URL to specify the field
        thingspeak_api_url = f'https://api.thingspeak.com/channels/2384494/fields/1.json?api_key=EJU2GGIUNTGCOV4S&results=2'
        response = requests.get(thingspeak_api_url)
        data = response.json()
        # Extract relevant data from the response (modify this based on your ThingSpeak channel structure)
        value = data['feeds'][0]['field' + field_name[-1]]
        return value
    except Exception as e:
        print(f"Error fetching data from ThingSpeak: {e}")
        return None

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if '最新合作廠商' in msg:
        message = imagemap_message()
        line_bot_api.reply_message(event.reply_token, message)
    elif '最新活動訊息' in msg:
        message = buttons_message()
        line_bot_api.reply_message(event.reply_token, message)
    elif '註冊會員' in msg:
        message = Confirm_Template()
        line_bot_api.reply_message(event.reply_token, message)
    elif '旋轉木馬' in msg:
        message = Carousel_Template()
        line_bot_api.reply_message(event.reply_token, message)
    elif '圖片畫廊' in msg:
        message = test()
        line_bot_api.reply_message(event.reply_token, message)
    elif '功能列表' in msg:
        message = function_list()
        line_bot_api.reply_message(event.reply_token, message)
    elif '溫度' in msg:
        # Fetch temperature from ThingSpeak
        temperature = fetch_thingspeak_data('temperature')
        if temperature is not None:
            # Respond with the temperature value
            message = TextSendMessage(text=f'目前溫度：{temperature} °C')
        else:
            message = TextSendMessage(text='無法取得溫度資訊')
        line_bot_api.reply_message(event.reply_token, message)
    elif '氣體' in msg:
        # Fetch smoke data from ThingSpeak
        smoke = fetch_thingspeak_data('smoke')
        if smoke is not None:
            # Respond with the smoke value
            message = TextSendMessage(text=f'目前氣體濃度：{smoke}')
        else:
            message = TextSendMessage(text='無法取得氣體濃度資訊')
        line_bot_api.reply_message(event.reply_token, message)
    else:
        message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
