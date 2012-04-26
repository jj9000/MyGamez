#!/usr/bin/env python

import cherrypy
import os
from lib.WebRoot import WebRoot
import sys
import socket
import sched
import time
import threading
import thread
import datetime
import lib.GameTasks
import ConfigParser
import cherrypy.process.plugins
from cherrypy.process.plugins import Daemonizer,PIDFile
from lib.ConfigFunctions import CheckConfigForAllKeys
from lib.DBFunctions import ValidateDB,AddWiiGamesIfMissing,AddXbox360GamesIfMissing,AddComingSoonGames
from lib.Logger import LogEvent
import cherrypy.lib.auth_basic
from lib.FolderFunctions import *

app_path = os.path.dirname(os.path.abspath("__FILE__"))
config_path = os.path.join(app_path,'Gamez.ini')

class RunApp():


    def RunWebServer(self):
        LogEvent("Generating CherryPy configuration")
        cherrypy.config.update(config_path)
        config = ConfigParser.RawConfigParser()
        config.read('Gamez.ini')
        # Set Webinterface Path
        css_webinterface = "css/" + config.get('SystemGenerated','webinterface').replace('"','')
        
        css_path = os.path.join(app_path,css_webinterface)
        DebugLogEvent("CSS Path : [ " + css_path + " ]")
        images_path = os.path.join(app_path,'images')
        navigation_images_path = os.path.join(css_path,'navigation_images')
        datatables_images_path = os.path.join(css_path,'datatables_images')
        js_path = os.path.join(app_path,'js')
        theme_path = os.path.join(css_path,'redmond')
        theme_images_path = os.path.join(theme_path,'images')
        username = config.get('global','user_name').replace('"','')
        password = config.get('global','password').replace('"','')
        useAuth = False
        if(username <> "" or password <> ""):
            useAuth = True          	
        userPassDict = {username:password}  
        checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(userPassDict)
        conf = {
        	  '/':{'tools.auth_basic.on':useAuth,'tools.auth_basic.realm':'Gamez','tools.auth_basic.checkpassword':checkpassword},
                '/api':{'tools.auth_basic.on':False},
                '/css': {'tools.staticdir.on':True,'tools.staticdir.dir':css_path},
                '/js':{'tools.staticdir.on':True,'tools.staticdir.dir':js_path},
                '/css/redmond':{'tools.staticdir.on':True,'tools.staticdir.dir':theme_path},
                '/css/redmond/images':{'tools.staticdir.on':True,'tools.staticdir.dir':theme_images_path},
                '/css/navigation_images':{'tools.staticdir.on':True,'tools.staticdir.dir':navigation_images_path},
                '/css/datatables_images':{'tools.staticdir.on':True,'tools.staticdir.dir':datatables_images_path},
            }
         
        isSabEnabled = config.get('SystemGenerated','sabnzbd_enabled').replace('"','')
        if(isSabEnabled == "1"):
            LogEvent("Generating Post Process Script")
            GenerateSabPostProcessScript()
        RunGameTask()

        LogEvent("Getting download interval from config file and invoking scheduler")
        config = ConfigParser.RawConfigParser()
        config.read('Gamez.ini')
        interval = config.get('Scheduler','download_interval').replace('"','')
        updateGameListInterval = config.get('Scheduler','game_list_update_interval').replace('"','')
        fInterval = float(interval)
        fUpdateGameListInterval = float(updateGameListInterval)
        try:
            LogEvent("Setting up download scheduler")
            gameTasksScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine,RunGameTask,fInterval)
            gameTasksScheduler.subscribe()
            LogEvent("Setting up game list update scheduler")
            gameListUpdaterScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine,RunGameListUpdaterTask,fUpdateGameListInterval)
            gameListUpdaterScheduler.subscribe()
            LogEvent("Setting up folder processing scheduler")
            folderProcessingScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine,RunFolderProcessingTask,float(900))
            folderProcessingScheduler.subscribe()
            LogEvent("Starting the Gamez web server")
            cherrypy.quickstart(WebRoot(app_path),'/',config=conf)
        except KeyboardInterrupt:
            LogEvent("Shutting down Gamez")
            if(isToDaemonize == 1):    
                daemon.unsubscribe()
            sys.exit()
        
def GenerateSabPostProcessScript():
    sys_name = socket.gethostname()
    gamezWebHost = socket.gethostbyname(sys_name)
    gamezApi = config.get('SystemGenerated','api_key').replace('"','')
    gamezWebport = config.get('global','gamez_port').replace('"','')
    realWebport = str(cherrypy.config.get('server.socket_port', gamezWebport))
    gamezBaseUrl = "http://" + gamezWebHost + ":" + realWebport + "/"
    postProcessPath = os.path.join(app_path,'postprocess')
    postProcessScript = os.path.join(postProcessPath,'gamezPostProcess.py')
    file = open(postProcessScript,'w')
    file.write('#!/usr/bin/env python')
    file.write("\n")
    file.write('import sys')
    file.write("\n")
    file.write('import urllib')
    file.write("\n")
    file.write("filePath = str(sys.argv[1])")
    file.write("\n")
    file.write('fields = str(sys.argv[3]).split("-")')
    file.write("\n")
    file.write('gamezID = fields[0].replace("[","").replace("]","").replace(" ","")')
    file.write("\n")
    file.write("status = str(sys.argv[7])")
    file.write("\n")
    file.write("downloadStatus = 'Wanted'")
    file.write("\n")
    file.write("if(status == '0'):")
    file.write("\n")
    file.write("    downloadStatus = 'Downloaded'")
    file.write("\n")
    file.write('url = "' + gamezBaseUrl + 'api?api_key=' + gamezApi + '&mode=UPDATEREQUESTEDSTATUS&db_id=" + gamezID + "&status=" + downloadStatus')
    file.write("\n")
    file.write('responseObject = urllib.FancyURLopener({}).open(url)')
    file.write("\n")
    file.write('answer = responseObject.read()')
    file.write("\n")
    file.write('responseObject.close()')
    file.write("\n")
    file.write("print(answer)")
    file.write("\n")
    file.write("exit(0)")
    file.close
    LogEvent("Setting permissions on post process script")
    cmd = "chmod +x '" + postProcessScript + "'"
    os.system(cmd)

def RunGameTask():
    try:
        isDebugEnabled = config.get('global','debug_enabled').replace('"','')
        nzbMatrixUser = config.get('NZBMatrix','username').replace('"','')
        nzbMatrixApi = config.get('NZBMatrix','api_key').replace('"','')
        sabnzbdHost = config.get('Sabnzbd','host').replace('"','')
        sabnzbdPort = config.get('Sabnzbd','port').replace('"','')
        sabnzbdApi = config.get('Sabnzbd','api_key').replace('"','')
        sabnzbdCategory = config.get('Sabnzbd','category').replace('"','')
        newznabWiiCat = config.get('Newznab','wii_category_id').replace('"','')
        newznabXbox360Cat = config.get('Newznab','xbox360_category_id').replace('"','')
        newznabPS3Cat = config.get('Newznab','ps3_category_id').replace('"','')
        newznabPCCat = config.get('Newznab','pc_category_id').replace('"','')
        newznabApi = config.get('Newznab','api_key').replace('"','')
        newznabHost = config.get('Newznab','host').replace('"','')
        newznabPort = config.get('Newznab','port').replace('"','')
        isSabEnabled = config.get('SystemGenerated','sabnzbd_enabled').replace('"','')
        isNzbMatrixEnabled = config.get('SystemGenerated','nzbmatrix_enabled').replace('"','')
        isNewznabEnabled = config.get('SystemGenerated','newznab_enabled').replace('"','')
        isNzbBlackholeEnabled = config.get('SystemGenerated','blackhole_nzb_enabled').replace('"','')
        nzbBlackholePath = config.get('Blackhole','nzb_blackhole_path').replace('"','')
        isTorrentBlackholeEnabled = config.get('SystemGenerated','blackhole_torrent_enabled').replace('"','')
        isTorrentKATEnabled = config.get('SystemGenerated','torrent_kat_enabled').replace('"','')
        torrentBlackholePath  = config.get('Blackhole','torrent_blackhole_path').replace('"','')
        manualSearchGame = ''
        LogEvent("Searching for games")
        lib.GameTasks.GameTasks().FindGames(manualSearchGame,nzbMatrixUser,nzbMatrixApi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbMatrixEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,torrentBlackholePath)
    except:
        errorMessage = "Major error occured when running scheduled tasks"
        for message in sys.exc_info():
            errorMessage = errorMessage + " - " + str(message)
        LogEvent(errorMessage)

def RunGameListUpdaterTask():
    try:
        LogEvent("Updating Game Lists")
        AddWiiGamesIfMissing()
        LogEvent("Wii Game List Updated")
        AddXbox360GamesIfMissing()
        LogEvent("XBOX 360 Game List Updated")
        AddComingSoonGames
        LogEvent("Coming Soon Game List Updated")
    except:
        errorMessage = "Major error occured when running Update Game List scheduled tasks"
        for message in sys.exc_info():
            errorMessage = errorMessage + " - " + str(message)
        LogEvent(errorMessage)

def RunFolderProcessingTask():
    try:
        ScanFoldersToProcess()
    except:
        errorMessage = "Error occurred while processing folders"
        for message in sys.exc_info():
            errorMessage = errorMessage + " - " + str(message)
        LogEvent(errorMessage)

def ComandoLine():    
    from optparse import OptionParser
 
    p = OptionParser()
    p.add_option('-d', '--daemonize', action = "store_true",
                 dest = 'daemonize', help = "Run the server as a daemon")
    p.add_option('--debug', action = "store_true",
                 dest = 'debug', help = "Enable Debug Log")
    p.add_option('--pidfile',
                 dest = 'pidfile', default = None,
                 help = "Store the process id in the given file")
    p.add_option('--port',
                 dest = 'port', default = None,
                 help = "Force webinterface to listen on this port")

    options, args = p.parse_args()

    # Daemonize
    if options.daemonize:
       print "------------------- Preparing to run in daemon mode -------------------"
       LogEvent("Preparing to run in daemon mode")  
       daemon = Daemonizer(cherrypy.engine)
       daemon.subscribe()
   
    # Debug
    if options.debug:
        config.set('global','debug_enabled','1')
        print "------------------- Gamez run in Debug -------------------"
        LogEvent('Gamez run in Debug')
    
    # Set port
    if options.port:
        print "------------------- Port manual set to " + options.port + " -------------------"
        port = int(options.port)
    else:    
        port = int(config.get('global','gamez_port'))
     
    # PIDfile
    if options.pidfile:
        print "------------------- Set PIDfile to " + options.pidfile + " -------------------"
        PIDFile(cherrypy.engine, options.pidfile).subscribe()

    # update config for cherrypy
    cherrypy.config.update({
                                'global': {
                                           'server.socket_port': port
                                          }
                            })


if __name__ == '__main__':
    app_path = sys.path[0]
    ValidateDB()
    LogEvent("Checking config file for completeness")
    CheckConfigForAllKeys(app_path)
    config = ConfigParser.RawConfigParser()
    configFilePath = os.path.join(app_path,'Gamez.ini')
    config.read(configFilePath)
    sabnzbdHost = config.get('Sabnzbd','host').replace('"','')
    sabnzbdPort = config.get('Sabnzbd','port').replace('"','')
    sabnzbdApi = config.get('Sabnzbd','api_key').replace('"','')
    LogEvent("Attempting to get download completed directory from Sabnzbd")
    ComandoLine()
    sabCompleted = lib.GameTasks.GameTasks().CheckSabDownloadPath(sabnzbdApi,sabnzbdHost,sabnzbdPort)
    if(sabCompleted <> ""):
    	LogEvent("Setting Value")
    	config.set('Folders','sabnzbd_completed','"' + sabCompleted + '"')
    	LogEvent("Trying to save")
    	with open(configFilePath,'wb') as configFile:
            config.write(configFile)    
  
    RunApp().RunWebServer()
