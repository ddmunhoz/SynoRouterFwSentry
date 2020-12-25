#https://github.com/ddmunhoz/XXX
FROM python:3

ENV ROUTER ""

ENV USER ""

ENV PASS  ""

ENV RULES ""

ENV INTERVAL ""

ENV INTERVAL_DEVICE_MONITOR ""

ENV MONITORED_DEVICES ""

ENV NOTIFY ""

ENV DEBUG ""

ENV TELEGRAM_CHAT_ID ""

ENV TELEGRAM_BOT_ID ""

RUN mkdir ./SynoRouterFWSentry

RUN mkdir ./SynoRouterFWSentry/logs

ADD . ./SynoRouterFWSentry

RUN pip install --no-cache-dir -r ./SynoRouterFWSentry/requirements.txt

CMD ["sh", "-c", "python  ./SynoRouterFWSentry/synoRouterFwSentry.py -router $ROUTER -user $USER -pass $PASS -rules $RULES -interval $INTERVAL -intervalDeviceMonitor $INTERVAL_DEVICE_MONITOR -monitoredDevices $MONITORED_DEVICES -notify $NOTIFY -debug $DEBUG -telegramChatId $TELEGRAM_CHAT_ID -telegramBotId $TELEGRAM_BOT_ID"]

