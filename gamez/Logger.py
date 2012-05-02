import DBFunctions
import os
import ConfigParser

confFile = os.path.join(os.path.dirname(os.path.abspath("__FILE__")),'Gamez.ini')
config = ConfigParser.RawConfigParser()
config.read(confFile)

def LogEvent(message):
     DBFunctions.AddEventToDB(message)
     return

def DebugLogEvent(message):
     message = "DEBUG : " + message
     if(config.get('global','debug_enabled').replace('"','') == "1"): 
         DBFunctions.AddEventToDB(message)
     return

def ClearLog():
    ClearDBLog()
    return