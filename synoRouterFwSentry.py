import os
from os.path import dirname
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timezone
import time as altTime
import time
from tools.messaging import telegramBot
from tools.synoRouter import synoRouter

#Parse parameters
parser = argparse.ArgumentParser(description='Synology Router FW rules Sentry')
parser.add_argument('-router',help='Router IP and Port Ie.: https://10.0.0.1:7778', required=True)
parser.add_argument('-user',help='Router account username', required=True)
parser.add_argument('-pass',help='Router account password', required=True)
parser.add_argument('-monitoredDevices',help='Hosts to be monitored', required=True)
parser.add_argument('-rules',help='Firewall rules to modify', required=True)
parser.add_argument('-interval',help='Interval between collection in seconds', required=True)
parser.add_argument('-intervalDeviceMonitor',help='Interval between collection in seconds', required=True)
parser.add_argument('-notify',help='Send notifications over Telegrams Channel when FW rules are changed', required=True)
parser.add_argument('-debug',help='Send notifications over Telegrams when bugs occur', required=True)
parser.add_argument('-telegramChatId',help='Telegram Chat Id where notifications will be sent', required=False)
parser.add_argument('-telegramBotId',help='Telegram Bot Id used to send notifications', required=False)

args=vars(parser.parse_args())
firstRun = True

#Router Info
routerAddr = args['router']
routerUsername = args['user']
routerPassword = args['pass']
monitoredDevices = args['monitoredDevices']
firewalRules = args['rules'].lower()
telegramDebugger = args['debug'].lower() == 'true'
telegramNotifier = args['notify'].lower() == 'true'
telegramChatId = args['telegramChatId']
telegramBotId = args['telegramBotId']

#Collection and DB params
loopInterval = int(args['interval'])
intervalDeviceMonitor = int(args['intervalDeviceMonitor'])

#Instantiate Bot
notifyBot = None
if telegramNotifier is True:
    notifyBot = telegramBot.telegramBot(telegramChatId,telegramBotId)

#Initiate logging
logPath = (os.path.dirname(os.path.realpath(__file__))) + '/logs/crashLog.txt'
def logSetup():
    #formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(name)s %(message)s')
    #fh = TimedRotatingFileHandler('crashLog.txt', 'midnight',1)
    #fh.suffix = "%Y-%m-%d"
    logger = logging.getLogger('crashLog')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                    datefmt='%m-%d-%y %H:%M:%S')
    fh = TimedRotatingFileHandler(logPath, when='S', interval=5)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

logger = logSetup()

#Clocks
logDeviceMonitor = time.time()

#Router connection initialization
routerConnection = synoRouter(ip=routerAddr, username=routerUsername, password=routerPassword, monitoredDevices=monitoredDevices, rules=firewalRules, notifier=notifyBot)

def crashReporter(message):
    crashLog = open(logPath,'r')
    if telegramDebugger is True:
        notifyBot.sendMessage(f'Syno Router FW Sentry says: {message}',type = 'file',binPayload = crashLog)

def now_iso():
    now_iso = datetime.now(timezone.utc).astimezone().isoformat()
    return now_iso

def mainRunner():
    global firstRun
    global logMonitoredDevicesTime

    try:
        starttime=altTime.time()
        print('\n[---> Starting Device Monitoring ----------------------] [' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']')
        
        if (time.time() - intervalDeviceMonitor > logDeviceMonitor) or firstRun == True:
            print('\n### Device Monitoring #######\n')
            routerConnection.huntMonitoredDevices()
            routerConnection()
            logMonitoredDevicesTime = time.time()
        else:
            nextRunWindow = datetime.fromtimestamp(logDeviceMonitor + intervalDeviceMonitor).strftime('%Y-%m-%d %H:%M:%S')
            print(f'\n*** Device Monitoring - Next run Window -> {nextRunWindow}\n')

       
        print('\n[<--- Execution finished ------------------------------] [' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']')
        altTime.sleep(int(loopInterval) - ((altTime.time() - starttime) % int(loopInterval)))

        firstRun = False
    except Exception as error:
            logger.exception(error)
            crashReporter('I tried to mainRunner, but I failed!')
            return False

#Auth and Banner
print('# ---------------------> Starting data Collector ----------------------')
print('# - Loop Interval: ' + str(loopInterval) + ' seconds')
print('# - Devices Monitored: ' + monitoredDevices)
print('# - Device Monitor Interval: ' + str(intervalDeviceMonitor) + ' seconds')
print('# - Router: ' + routerAddr )
print('# - Router username: ' + routerUsername)
print('# - Firewall Rules: ' + firewalRules)
print('# - Telegram Notifier: ' + str(telegramNotifier))
print('# - Telegram Debugger: ' + str(telegramDebugger))
print('# - Telegram ChatID: ' + telegramChatId)
print('# - Telegram BotId: ' + telegramBotId)
print('#######################################################################')

#try:
#    raise Exception('test')
#except Exception as error:
#    logger.exception(error)
#    crashReporter()

while True:
    mainRunner()