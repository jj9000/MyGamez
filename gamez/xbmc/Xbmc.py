import os
import re
import base64
import cherrypy
import urllib
import urllib2
from gamez.Logger import *
import ConfigParser

             
def xbmcsend(host, command, username, password, appPath):
              
            url = 'http://%s/xbmcCmds/xbmcHttp/?%s' % (host, urllib.urlencode(command))

            try:
                req = urllib2.Request(url)
                if password:
                    authHeader = "Basic %s" % base64.encodestring('%s:%s' % (username, password))[:-1]
                    req.add_header("Authorization", authHeader)

                handle = urllib2.urlopen(req, timeout = 10)
                response = handle.read()
            except Exception, e:
                LogEvent("Couldn't sent command to XBMC. %s" % e)
                return False

            LogEvent('XBMC notification to %s successful.' % host)
            return response

def xbmcnotify(message,appPath):

        config = ConfigParser.RawConfigParser()
        configFilePath = os.path.join(appPath,'Gamez.ini')
        config.read(configFilePath)
        username = config.get('Notifications','xbmc_username').replace('"','')
        password = config.get('Notifications','xbmc_password').replace('"','')
        hosts = config.get('Notifications','xbmc_hosts').replace('"','')
        hosts = re.split(';|,',hosts)   
       
        DebugLogEvent("XBMC hosts " + str(hosts))
        for host in hosts:
              command = {'command': 'ExecBuiltIn', 'parameter': 'Notification(GAMEZ, %s, 5000,)' % message}
              LogEvent(host)
              xbmcsend(host, command, username, password, appPath)
