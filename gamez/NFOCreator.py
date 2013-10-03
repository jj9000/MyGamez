import os
import sys
import urllib
import urllib2
import ConfigParser

import gamez

from gamez.Logger import LogEvent,DebugLogEvent
import DBFunctions
from gamez.TheGamesDBSearcher import GetXmlFromTheGamesDB



# This writes a nfo file to the Downloaded folder
# Notice! At the moment only Sabnzbd is supportet

def WriteNFO(game_title='',game_system='',game_description='',game_publisher='',game_developer='',game_genre='',game_release=''):

    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    sabnzbd_category = config.get('Sabnzbd','category').replace('"','')
    
    # Search for Gamefolder
    gamelist = os.listdir(sabnzbd_category)
    for game in gamelist:
        if game.find(game_title) != -1:
          gamefoldername = game
          DebugLogEvent("Gamefoldername: " + str(gamefoldername))
    try:
        # Lets write the file
        nfofile = os.path.join(os.path.apspath(sabnzbd_category),gamefoldername)
        file = open(nfofile,'w')
        file.write('<game>')
        file.write("\n")
        file.write('     <title>' + str(game_title) + '</title>')
        file.write("\n")
        file.write('     <platform>' + str(game_system) + '</platform>')
        file.write("\n")
        file.write('     <year>' + str(game_release) + '</year>')
        file.write("\n")
        file.write('     <plot>' + str(game_description) + '</plot>')
        file.write("\n")
        file.write('     <publisher>' + str(game_publisher) + '</publisher>')
        file.write("\n")
        file.write('     <developer>' + str(game_developer) + '<developer>')
        file.write("\n")
        file.write('     <genre>' + str(game_genre) + '</genre>')
        file.write("\n")
        file.write('     <release>' + str(game_release) + '</release>')
        file.write("\n")
        file.write('</game>')
        file.write("\n")
        file.write("exit(0)")
        file.close
        LogEvent("Writing of NFO file succses")
        #cmd = "chmod +x '" + nfofile + "'"
        #os.system(cmd)
    except:
        LogEvent("ERROR: !!!!!!NFO File writing faild!!!!!!")

 

def CreatNFO(dbid):
     term = ""
     system = DBFunctions.GetRequestedGameSystem(dbid)
     TheGamesDB_id = DBFunctions.GetRequestedTheGamesDBid(dbid)
     if(TheGamesDB_id != ""):
         try:
              game_title = dom.getElementsByTagName('GameTitle')#.toxml()
              game_title = game_title.replace('<GameTitle>','').replace('</GameTitle>','')
              game_system = dom.getElementsByTagName('Platform')#.toxml()
              game_system = game_system.replace('<Platform>','').replace('</Platform>','')
              game_descripton = dom.getElementsByTagName('Overview')#.toxml()
              game_descripton = descripton.replace('<Overview>','').replace('</Overview>','')
              game_publisher = dom.getElementsByTagName('Publisher')#.toxml()
              game_publisher = publisher.replace('<Publisher>','').replace('</Publisher>','')
              game_developer = dom.getElementsByTagName('Developer')#.toxml()
              game_developer = developer.replace('<Developer>','').replace('</Developer>','')
              game_genre = dom.getElementsByTagName('genre')#.toxml()
              game_genre = genre.replace('<genre>','').replace('</genre>','')
              game_release = dom.getElementsByTagName('ReleaseDate')#.toxml()
              game_release = release.replace('<ReleaseDate>','').replace('</ReleaseDate>','')

              DebugLogEvent("Titel: " + str(game_title) + " System: " + game_system + " Description: " + game_description + " Publischer: " + game_publisher + " Developer: " + game_developer + " Genre: "+ game_genre + " Release: " + game_release)
              WriteNFO(game_title, game_system, game_description, game_publisher, game_developer, game_genre, game_release)
         except:
              LogEvent("ERROR: !!!!!!NFO creating faild!!!!!!")
     else:
          LogEvent("Can not create NFO file. There is no ID from TheGamesdb.net")    
    
