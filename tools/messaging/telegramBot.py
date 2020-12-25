import requests
import base64
import urllib
import io

class telegramBot:
    """Simple class to send messages using Telegram Bot API """

    def __init__(self, chatId, botToken):
        self._chatId = chatId
        self._botToken = botToken
    
    def getIpInformation(self, ip):
        ipPayloadResponse = f'http://ip-api.com/json/{ip}'
        response = requests.get(ipPayloadResponse)
        return response.json()

    def getIpLocationMap(self, lon, lat, action = 'link'):
        if action == 'image':
            #&zoom=17&size=1440x900&maptype=hybrid&
            ipPayloadResponse = f'https://maps.googleapis.com/maps/api/staticmap?&zoom=14&size=350x350&center={lat},{lon}&key=AIzaSyDIJ9XX2ZvRKCJcFRrl-lRanEtFUow4piM'
            response = requests.get(ipPayloadResponse)
            #uri = ("data:" + 
            #response.headers['Content-Type'] + ";" +
            #"base64," + str(base64.b64encode(response.content).decode("utf-8")))
            return response.content

        if action == 'hybrid':
            return f'https://maps.googleapis.com/maps/api/staticmap?&zoom=17&size=1440x900&maptype=hybrid&markers=icon:https://www.gstatic.com/earth/images/stockicons/190201-2016-animal-paw_4x.png|{lat},{lon}&key=AIzaSyDIJ9XX2ZvRKCJcFRrl-lRanEtFUow4piM'

        if action == 'link':
                return f'https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=13&size=300x300&key=AIzaSyDIJ9XX2ZvRKCJcFRrl-lRanEtFUow4piM'
    
    def sendMessage(self, bot_message, silently = False, type = 'text', binPayload = None):
        if type == 'text':
            send_text = f'https://api.telegram.org/bot{self._botToken}/sendMessage?chat_id={self._chatId}&parse_mode=markdown&text={bot_message}&disable_notification={silently}'
            response = requests.get(send_text)
            return response.json()

        if type == 'file':
            send_text = f'https://api.telegram.org/bot{self._botToken}/sendDocument?chat_id={self._chatId}&parse_mode=markdown&caption={bot_message}&disable_notification={silently}'
            response = requests.post(send_text, files={'document': binPayload})
            return response.json()
        
        if type == 'image':
            send_text = f'https://api.telegram.org/bot{self._botToken}/sendPhoto?chat_id={self._chatId}&parse_mode=markdown&caption={bot_message}&disable_notification={silently}'
            response = requests.post(send_text, files={'photo': binPayload})
            return response.json()