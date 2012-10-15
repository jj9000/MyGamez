import DBFunctions
import os
import ConfigParser
import gamez


def LogEvent(message):
     DBFunctions.AddEventToDB(message)
     return

def DebugLogEvent(message):
     config = ConfigParser.RawConfigParser()
     configfile = os.path.abspath(gamez.CONFIG_PATH)
     config.read(configfile)
     message = "DEBUG : " + message

     if(config.get('global','debug_enabled').replace('"','') == "1"): 
         DBFunctions.AddEventToDB(message)
     return

def ClearLog():
    ClearDBLog()
    return