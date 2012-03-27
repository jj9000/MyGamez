import os
import sqlite3
import sys
import datetime
from Logger import LogEvent
import urllib2
import json
import DBFunctions
from xml.dom.minidom import parseString

def AddGamefromTheGameDB(term,system):
    gamefile = None
    gamedata = None
    tagnbr = 0
    if(system == 'PS3'):
       Platform = "Sony+Playstation+3"
    elif(system == 'PC'):
       Platform = "PC"
    elif(system == 'Wii'):
       Platform = "Nintendo+Wii"
    elif(system == 'Xbox360'):
       Platform = "Microsoft+Xbox+360"
    gamefile = urllib2.urlopen('http://thegamesdb.net/api/GetGame.php?name=' + term.replace(' ','+') + '&platform=' + Platform)
    #convert to string:
    gamedata = gamefile.read()
    #close file because we dont need it anymore:
    gamefile.close()
    dom = parseString(gamedata)
    TagElements = dom.getElementsByTagName("Game")
    for d in TagElements:
        dom = parseString(gamedata)
        xmlTagTitle = dom.getElementsByTagName('GameTitle')[tagnbr].toxml()
        xmlGameTitle=xmlTagTitle.replace('<GameTitle>','').replace('</GameTitle>','')
        LogEvent("Find Game: " + xmlGameTitle)
        xmlTagid = dom.getElementsByTagName('id')[tagnbr].toxml()
        xmlGameid=xmlTagid.replace('<id>','').replace('</id>','')
        game_name = xmlGameTitle
        gamefileid = urllib2.urlopen('http://thegamesdb.net/api/GetGame.php?id=' + xmlGameid) 
        LogEvent('http://thegamesdb.net/api/GetGame.php?id=' + xmlGameid)
        gamedataid = gamefileid.read()
        gamefileid.close()
        dom2 = parseString(gamedataid)
        game_type = GetDetailsgenre(dom2)
        game_cover_raw = GetDetailscover(dom2,system)
        game_cover = "http://thegamesdb.net/banners/" + game_cover_raw
        db_path = os.path.join(os.path.abspath(""),"Gamez.db")
        connection = sqlite3.connect(db_path)
        LogEvent("Adding PS3 Game [" + game_name.replace("'","''") + "] to Game List. Cover :" + game_cover.replace("'","''"))
        #LogEvent("There are "+ tagelements + "Elements") 
        if(game_name <> ''):
            sql = "INSERT INTO games (game_name,game_type,system,cover) values('" + game_name.replace("'","''") + "','" + game_type + "','" + system + "','" + game_cover + "')"
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            tagnbr = tagnbr + 1
      
def GetDetailsgenre(TheMoveDBurl):
    try:
        xmlTaggenre = TheMoveDBurl.getElementsByTagName('genre')[0].toxml()
        xmlGamegenre=xmlTaggenre.replace('<genre>','').replace('</genre>','')
        LogEvent("Found a Genre: " + xmlGamegenre)
        return str(xmlGamegenre)
    except:
        xmlGamegenre="Game"
        return xmlGamegenre


def GetDetailscover(TheMoveDBurl,system):
    try:
        xmlTagcover = TheMoveDBurl.getElementsByTagName('boxart')[0].toxml()  
        coverside=xmlTagcover.getAttribute('side')
        xmlGamecover=xmlTagcover.replace('<boxart(.*)>','').replace('</boxart>','')    
        LogEvent("Found a Cover: " + xmlGamecover + coverside)
        return str(xmlGamecover)
    except:
        if(system == "PS3"):
            xmlGamecover="_platformviewcache/platform/boxart/12-1.jpg"
        elif(system == "PC"):
            xmlGamecover="_platformviewcache/platform/boxart/1-1.jpg"
        else:
            xmlGamecover="None"
        return str(xmlGamecover)
