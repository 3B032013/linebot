from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

from linebot.models import TextSendMessage

import json
import requests
import logging

# 設定 log 檔案的名稱和格式
log_filename = 'app.log'
logging.basicConfig(filename=log_filename, level=logging.DEBUG)

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

def fetch_thingspeak_data(channel_id, api_key, field_name, results=1):
    try:
        thingspeak_api_url = f'https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}&results={results}'
        response = requests.get(thingspeak_api_url)
        data = response.json()

        logging.debug(f"ThingSpeak API Response: {data}")

        values = [entry.get(field_name) for entry in data.get('feeds', [])]
        return values
    except Exception as e:
        logging.error(f"Error fetching data from ThingSpeak: {e}")
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
    msg = event.message.text
    channel_id = '2384494'
    api_key = 'EJU2GGIUNTGCOV4S'
    if '溫度' in msg:
        # 取得thingspeak上的溫度值
        temperatures = fetch_thingspeak_data(channel_id, api_key, 'field1')
        if temperatures:
            message = TextSendMessage(text=f'目前溫度：{", ".join(map(str, temperatures))} °C')
        else:
            message = TextSendMessage(text='無法取得溫度資訊')
        line_bot_api.reply_message(event.reply_token, message)
    elif '氣體' in msg:
        # 取得thingspeak上的煙霧值
        smokes = fetch_thingspeak_data(channel_id, api_key, 'field2')
        if smokes:
            message = TextSendMessage(text=f'目前氣體濃度：{", ".join(map(str, smokes))}')
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
