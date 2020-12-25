# Syno router Firewall Sentry - WIP

This project aims to provide a simple way to switch Synology Router RT2600ac firewall/port forward
rules on/off based on a set of monitored devices.

###### Disclaimer

Feel free to fork and do as you please. All that I ask is to keep reference to the original code.
Also if you feel like contributing to it, write, push and let me know :)

###### Scenario example: 

Enable firewall rules **SSWAN1,SSWAN2(-rules)** and turn on port forwarding for the respective rules
when devices with MAC **41:DF:40:10:XD:E1 and 5A:11:53:1C:G6:B6(-monitoredDevices)** disconnect from the router.

Also, I would like to get a **notification(-notify)** over my Telegram Group chat when it happens,
my telegram chat id is **-769879789798(-telegramChatId)** and my telegram bot it is **9679697869876:jHSDkjJKnjkASD(-telegramBotId)**

my Synology router **username(-user)** is NotACiscoDevice and my **password(-pass)** for it is 1234567Change
my Synology **router IP and port is 10.0.0.1:5001(-router)**

I prefer the check tool to check for the **run window(-interval)** every 30 seconds and I want 
my router to be **pulled(-intervalDeviceMonitor) for data** every 60 seconds

I do not want **debug(-debug)** messages on my Telegram chat.

```
"-router","10.0.0.1:5001",
"-user","NotACiscoDevice",
"-pass","1234567Change",
"-rules","SSWAN1,SSWAN2",
"-interval","30",
"-intervalDeviceMonitor","60",
"-monitoredDevices","41:DF:40:10:XD:E1,5A:11:53:1C:G6:B6",
"-notify","True",
"-debug","False",
"-telegramChatId","-769879789798",
"-telegramBotId","9679697869876:jHSDkjJKnjkASD"
```
        

##  Docker - HOWTO :D

###### Build Image 

First git clone this repo by running the command git clone https://github.com/ddmunhoz/SynoRouterFwSentry.git

Enter the folder and run ```docker build --tag synorouterfwsentry:1.0 .```
Wait for docker to finish building your image.

###### Container launch CMD line

```
docker run --restart always -dt --name SynoRouterSentry \
-v /etc/localtime:/etc/localtime \
-e "ROUTER=10.0.0.1:5001" \
-e "USER=NotACiscoDevice" \
-e "PASS=1234567Change" \
-e "RULES=SSWAN1,SSWAN2" \
-e "INTERVAL=30" \
-e "INTERVAL_DEVICE_MONITOR=60" \
-e "MONITORED_DEVICES=41:DF:40:10:XD:E1,5A:11:53:1C:G6:B6" \
-e "NOTIFY=True"\
-e "DEBUG=False"\
-e "TELEGRAM_CHAT_ID=-769879789798"\
-e "TELEGRAM_BOT_ID=9679697869876:jHSDkjJKnjkASD"\
synorouterfwsentry:1.0

```

###### Environment variables breakdown

| Variable                 | Description                                                                 | Example                                                   | 
|      ---                 |        ---                                                                  |              ---                                          |
| ROUTER                   | IP and Port of your synology router. Make sure you have HTTPS enabled on it | 10.0.0.1:5001                                             |
| USER                     | Username with Admins rights on your router. Please follow this guide to create additional Admin users if required https://community.synology.com/enu/forum/2/post/127805                                                                                   | NotACiscoDevice                                          |
| PASS                     | Password of your Admin user                                                 | 1234567Change                                             |
| RULES                    | Comma separated RULES that you want to enable/disable when monitored devices connect/disconnect from the router. Pay attention to the fact that the tool will locate the port forward counterpart automatically for you if needed                        | SSWAN1,SSWAN2                                             |
| INTERVAL                 | Every X seconds the program loops and execute tasks - in seconds            | 30                                                        |
| INTERVAL_DEVICE_MONITOR  | Every X seconds your Router will be pulled for information.                 | 60                                                        |
| MONITORED_DEVICES        | List of MAC addresses comma separated of devices to be monitored            | 41:DF:40:10:XD:E1, 5A:11:53:1C:G6:B6                      |
| NOTIFY                   | Send message on telegram channel when rules are changed                     | True                                                      |
| DEBUG                    | Send message on telegram channel with attached log when a bug happens       | False                                                     |
| TELEGRAM_CHAT_ID         | Chat ID where message will be sent by the bot - Check this Guy guide https://www.youtube.com/watch?v=I-qI6jeLIsI on HOW TO CREATE A BOT                                                                                                      | -769879789798                                             |
| TELEGRAM_BOT_ID          | Telegram Bot ID that will be used to send messages - Check this Guy guide https://www.youtube.com/watch?v=I-qI6jeLIsI on HOW TO CREATE A BOT                                                                                                      | 9679697869876:jHSDkjJKnjkASD                              |

###### Comming soon...

| TODO                                | Description                                                                                         | 
|      ---                            |        ---                                                                                          | 
| Tests                               | Well.... for obvious reasons :D                                                                     |
| Exception handling and bug fixes    | Well.... for obvious reasons :D ^2                                                                  |
| Customize notification message      | Introduce option to customize notification message based on variables                               |
| Customize notification Alert        | Introduce option to deliver silent message                                                          |
| InfluxDB support                    | Dispatch data to influxDB to be graphed later using Grafana                                         |
| Move settings to Config file        | Move away from environment variables to a config file                                               |
| InfluxDB support                    | Dispatch data to influxDB to be graphed later using Grafana                                         |
| Grafana dashboard example           | Grafana dashboard to show status of rules                                                           |