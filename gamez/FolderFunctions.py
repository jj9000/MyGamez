import os
import shutil
import ConfigParser
import gamez

from Logger import *
from DBFunctions import *
from GameTasks import *

def ProcessFolder():
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    
    check = False
    folderPathSAB = config.get('Sabnzbd','folder').replace('"','')
    folderPathTorrent = config.get('Folders','torrent_completed').replace('"','')

    sabnzbd_enabled = config.get('SystemGenerated','process_sabnzbd_download_folder_enabled').replace('"','')
    torrent_enabled = config.get('SystemGenerated','process_torrent_download_folder_enabled').replace('"','')
    
    # Check for SABnzbd
    if(sabnzbd_enabled == '1'):
         if(folderPathSAB <> ''):
             folderPath = folderPathSAB
             ScanFolders(folderPath, check)
         else:
             LogEvent('"Completed Folder" for SABnzbd is not set. Please update your settings')

    #Check for Torrent
    if(torrent_enabled == '1'):
         if(folderPathTorrent <> ''):
             folderPath = folderPathTorrent
             check = True
             ScanFolders(folderPath, check)
         else:
             LogEvent('"Completed Folder" for Torrent is not set. Please update your settings')


def ScanFolders(folderPath,check):

    if(folderPath <> ''):
       LogEvent("Checking Folder for postprocessing")
       for record in GetRequestedGamesForFolderProcessing():
          game_name = record[0]
          system = record[1]    
          game_id = record[2]
          foldername = str(game_name) + " (" + str(system) + ")"
          for subdirs,dirs,files in os.walk(folderPath):
              for dir in dirs:
                 if(dir == foldername):
                      if(GameTasks().CheckStatusInSab(foldername)):
                           DebugLogEvent("Dirname [" + str(dir) +"]")
                           UpdateStatus(str(game_id),'Downloaded')
                      if(check): 
                           DebugLogEvent("Dirname [" + str(dir) +"]")
                           UpdateStatus(str(game_id),'Downloaded')
    else:
      LogEvent('"Postprocess" is not set. Please update your settings')   
