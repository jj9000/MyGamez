import ConfigParser
import os
import lib.prowlpy
from Logger import LogEvent,DebugLogEvent
import lib.gntp
import lib.notifo as Notifo
from gamez.xbmc.Xbmc import * 
import gamez

def HandleNotifications(status,message,appPath):
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    prowlApi = config.get('Notifications','prowl_api').replace('"','')
    growlHost = config.get('Notifications','growl_host').replace('"','')
    growlPort = config.get('Notifications','growl_port').replace('"','')
    growlPassword = config.get('Notifications','growl_password').replace('"','')
    notifoUsername = config.get('Notifications','notifo_username').replace('"','')
    notifoApi = config.get('Notifications','notifo_apikey').replace('"','')
    prowlEnabled = config.get('SystemGenerated','prowl_enabled').replace('"','')
    growlEnabled = config.get('SystemGenerated','growl_enabled').replace('"','')
    notifoEnabled = config.get('SystemGenerated','notifo_enabled').replace('"','')
    xbmcEnabled = config.get('SystemGenerated','xbmc_enabled').replace('"','')
    xbmcHosts = config.get('Notifications','xbmc_hosts').replace('"','')

    if(prowlEnabled == "1"):
        if(prowlApi <> ""):
            SendNotificationToProwl(status,message,prowlApi)  
        else:
            LogEvent("Missing Prowl API Key")
            
    if(growlEnabled == "1"):            
    	if(growlHost <> ""):
    	    SendNotificationToGrowl(status,message,growlHost,growlPort,growlPassword)  
    	else:
    	    LogEvent("Growl Settings Incomplete")
    
    if(notifoEnabled == "1"):
    	if(notifoUsername <> "" and notifoApi <> ""):
    	    SendNotificationToNotifo(status,message,notifoUsername,notifoApi)
    	else:
    	    LogEvent("Notifo Settings Incomplete")
    if(xbmcEnabled == "1"):
    	if(xbmcHosts <> ""):
    	    SendNotificationToXbmc(message,appPath,xbmcHosts)
    	else:
    	    LogEvent("XBMC Settings Incomplete. Please add a Host")
    return
    
def SendNotificationToProwl(status,message,prowlApi):
    prowl = prowlpy.Prowl(prowlApi)
    try:
    	prowl.add('Gamez',status,message,1,None,"http://www.prowlapp.com/")
    	LogEvent("Prowl Notification Sent")
    except Exception,msg:
    	LogEvent("Prowl Notification Error: " + msg)
    return
    
def SendNotificationToGrowl(status,message,growlHost,growlPort,growlPassword):
    if(growlPort == ""):
    	growlPort = "23053"
    try:
    	growl = lib.gntp.notifier.GrowlNotifier(applicationName = "Gamez",notifications = ["Gamez Download Alert"],defaultNotifications=["Gamez Download Alert"],hostname=growlHost,port=growlPort,password=growlPassword)
    	growl.register()
    	growl.notify(noteType="Gamez Download Alert",title=message,description=message,sticky=False,priority=1,)
    	LogEvent("Growl Notification Sent")
    except Exception,msg:
    	LogEvent("Growl Notification Error: " + msg)
    return   
    
def SendNotificationToNotifo(status,message,notifoUsername,notifoApiKey):
    notifoDict = {"to":notifoUsername,"msg":message,"label":"Gamez","title":"Gamez Download Alert"}
    try:
        notifo = Notifo(notifoUsername,notifoApiKey)
        LogEvent("Notifo Response: " + notifo.sendNotification(notifoDict))
    except Exception,msg:
    	LogEvent("Growl Notification Error: " + msg)
    return
    
def SendNotificationToXbmc(message,appPath,xbmcHosts):
    try:
        message = str(message)
        xbmcnotify(message,appPath)
        DebugLogEvent("Sending Notification Message to " + xbmcHosts)
    except Exception,msg:
        LogEvent("XBMC Notification Error: " + str(msg))
        return
