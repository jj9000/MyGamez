import base64
import urllib
import urllib2
import sys
import re
import ConfigParser
from gamez.Logger import *

def XbmcSend(message,appPath):
        
        #First we have a look into Configfile
        config = ConfigParser.RawConfigParser()
        configFilePath = os.path.join(appPath,'Gamez.ini')
        config.read(configFilePath)
        xbmcPassword = config.get('Notifications','xbmc_password').replace('"','')
        xbmcUsername = config.get('Notifications','xbmc_username').replace('"','')
        xbmcHosts = config.get('Notifications','xbmc_hosts').replace('"','')

        hosts = re.split(';|,',xbmcHosts)
        for host in hosts:
            url = 'http://' + host + ':8082/xbmcCmds/xbmcHttp/?command=execbuiltin(Notification(' + message.replace(':',',',1) + '))'
            DebugLogEvent("Executed URL:" + url)
            try:
               req = urllib2.Request(url)
               if xbmcPassword:
                    base64string = base64.encodestring('%s:%s' % (xbmcUsername, xbmcPassword)).replace('\n', '')
                    req.add_header("Authorization", "Basic %s" % base64string)
               handle = urllib2.urlopen(req)
               response = handle.read()
            except Exception, e:
               LogEvent("Couldn't send command to XBMC. %s\n" % e)

        LogEvent('XBMC notification to ' + host + ' successful.\n')
        return response


def XbmcTest(appPath):
        XbmcSend('Gamez Notification: This is a test notification.')