import requests
import json
from datetime import timezone, time, datetime, timedelta
import time as altTime
import logging
import urllib3
import sys
import argparse
from tools.messaging import telegramBot
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False


class synoRouter:
    """Holds information about Synology Router """

    def __init__(self, ip, username, password, monitoredDevices, rules, notifier = None):
            self.ip = ip
            self._authToken = None
            self._username = username
            self._password = password
            self.monitoredDevices = monitoredDevices
            self._activeMonitoredDevices = [] 
            self.notifier = notifier
            self.exceptionCounter = 0
            self.activeDevices = 0
            self.rules = rules

            if self._authToken is None:
                self._authRest()
            else:
                self.huntMonitoredDevices()
    
    def __call__(self):
        self.activeDevices = len(self._activeMonitoredDevices)
        if self.activeDevices > 0:
            print(f'\nTotal Active Devices: {self.activeDevices}\n')
            for activeMonitoredDevice in self._activeMonitoredDevices:
                print(f'\nHostname: {activeMonitoredDevice.Name}')
                print(f'Internal IP: {activeMonitoredDevice.Ip}')
                print(f'Mac: {activeMonitoredDevice.Mac}')
           
        else:
            print('No active Monitored Devices! skipping...')

    class clientDevice:
        """Holds information about Router Monitored devices"""
        def __init__(self, name, ip, mac):
            self.Name = name
            self.Ip = ip
            self.Mac = mac
    
    def _authRest(self):
        urlAuth = f'https://{self.ip}/webapi/auth.cgi'
        headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        body = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'api':'SYNO.API.Auth',
                'version':'2',
                'method':'login',
                'account':self._username,
                'passwd':self._password
                }   
        r = session.post(urlAuth, headers=headers, data=body)
        #Parse json response
        jsonDic = json.loads(r.text)
        if r.text == '{"error":{"code":401},"success":false}\n':
            return False
        else:
            #Get Auth Toke
            synoToken = jsonDic['data']['sid']
            self._authToken = synoToken
            return synoToken
    
    def _enumerateRouterDevices(self):
        url = f'https://{self.ip}/webapi/entry.cgi'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'api':'SYNO.Core.Network.NSM.Device',
                    'version':'1',
                    'method':'get',
                    'info':'online',
                    '_sid':self._authToken
                }   
        r = session.post(url, headers=headers, data=body)
        jsonDic = json.loads(r.text)
        result = jsonDic['data']['devices']
        return result

    def _getFirewallState(self):
        url = f'https://{self.ip}/webapi/entry.cgi'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'api':'SYNO.Core.Security.Firewall.Rules',
                    'version':'2',
                    'method':'get',
                    '_sid':self._authToken
                }   
        r = session.post(url, headers=headers, data=body)
        jsonDic = json.loads(r.text)
        firewallRules  = jsonDic['data']['rules']
        firewallPolicy = jsonDic['data']['default_policy']
        return firewallRules, firewallPolicy

    def _setFirewallState(self, state):
        rulesChanged = False
        changedRules = []

        #Get Firewall State
        firewallState = self._getFirewallState()

        #Change rules State
        for ruleInFirewall in firewallState[0]:
            for ruleInRequest in self.rules.split(','):
                if ruleInFirewall['name'].lower() == ruleInRequest:
                    if ruleInFirewall['enabled'] != state:
                        ruleInFirewall['enabled'] = state
                        rulesChanged = True
                        changedRules.append(ruleInFirewall)

        if rulesChanged == True:
            url = f'https://{self.ip}/webapi/entry.cgi'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            body = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'api':'SYNO.Core.Security.Firewall.Rules',
                        'version':'2',
                        'method':'set',
                        'rules': json.dumps(firewallState[0]),
                        'default_policy': json.dumps(firewallState[1]),
                        '_sid':self._authToken
                    }   
            r = session.post(url, headers=headers, data=body)
            jsonDic = json.loads(r.text)
            print()
            return changedRules

    def _getFirewallPortFoward(self):
        url = f'https://{self.ip}/webapi/entry.cgi'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'api':'SYNO.Core.Network.Router.PortForward',
                    'version':'1',
                    'method':'get',
                    '_sid':self._authToken
                }   
        r = session.post(url, headers=headers, data=body)
        jsonDic = json.loads(r.text)
        firewallPortFowardRules  = jsonDic['data']['rules']
        return firewallPortFowardRules

    def _setFirewallPortFoward(self, state, fwRules):
        rulesChanged = False

        #Get Firewall State
        firewallPortFowardState = self._getFirewallPortFoward()

        #Change rules State
        for ruleInFirewall in firewallPortFowardState:
            for ruleInRequest in fwRules:
                if ruleInFirewall['sourcePort'] == ruleInRequest['dst_port_value']:
                    if ruleInFirewall['enabled'] != state:
                        ruleInFirewall['enabled'] = state
                        rulesChanged = True

        if rulesChanged == True:
            url = f'https://{self.ip}/webapi/entry.cgi'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            body = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'api':'SYNO.Core.Network.Router.PortForward',
                        'version':'1',
                        'method':'set',
                        'rules': json.dumps(firewallPortFowardState),
                        '_sid':self._authToken
                    }   
            r = session.post(url, headers=headers, data=body)
            jsonDic = json.loads(r.text)
            print()

    def huntMonitoredDevices(self):
            snapshotActiveMonitoredDevices = self._activeMonitoredDevices 
            disconnectedDevices = []
            newConnectedDevices = []
            self._activeMonitoredDevices = []

            connectedDevices = self._enumerateRouterDevices()
            if len(connectedDevices) > 0:
                for device in connectedDevices:   
                    for monitoredDevice in self.monitoredDevices.split(','):
                        if device['mac'] == monitoredDevice:
                            onlineMonitoredDevice = self.clientDevice(device['hostname'],device['ip_addr'],device['mac'])
                            self._activeMonitoredDevices.append(onlineMonitoredDevice)

            self.activeDevices = len(self._activeMonitoredDevices)

            if self.activeDevices != len(self.monitoredDevices.split(',')):
                fwRules = self._setFirewallState(True)
                if fwRules is not None:
                    self._setFirewallPortFoward(True, fwRules)

                    if self.notifier is not None:
                        for snapDevice in snapshotActiveMonitoredDevices:
                            if snapDevice.Name not in [o.Name for o in self._activeMonitoredDevices]:
                                disconnectedDevices.append(snapDevice)

                        strDisconnectedDevices = [o.Name for o in disconnectedDevices]
                        strDisconnectedDevices = ','.join(strDisconnectedDevices)
                        message = f'📟 Opening VPN ports since {strDisconnectedDevices} left the perimeter'
                        self.notifier.sendMessage(f'{message}',type = 'text')

            else:
                fwRules = self._setFirewallState(False)
                if fwRules is not None:
                    self._setFirewallPortFoward(False, fwRules)

                    if self.notifier is not None:
                        for clientDevice in self._activeMonitoredDevices:
                            if clientDevice.Name not in [o.Name for o in snapshotActiveMonitoredDevices]:
                                newConnectedDevices.append(clientDevice)

                        strConnectedDevices = [o.Name for o in newConnectedDevices]
                        strConnectedDevices = ','.join(strConnectedDevices)

                        message = f'📟 Closing VPN ports since {strConnectedDevices} entered the perimeter'
                        self.notifier.sendMessage(f'{message}',type = 'text')