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
    fakeid = "fake"
    tagnbr = 0
    TheGameDBxml = GetXmlFromTheGameDB(term,system,fakeid)
    TagElements = TheGameDBxml.getElementsByTagName("Game")
    for d in TagElements:
        xmlTagTitle = TheGameDBxml.getElementsByTagName('GameTitle')[tagnbr].toxml()
        xmlGameTitle=xmlTagTitle.replace('<GameTitle>','').replace('</GameTitle>','')
        LogEvent("Found Game: " + xmlGameTitle)
        xmlTagid = TheGameDBxml.getElementsByTagName('id')[tagnbr].toxml()
        xmlGameid=xmlTagid.replace('<id>','').replace('</id>','')
        TheGameDBxml_byid = GetXmlFromTheGameDB(term,system,xmlGameid)
        game_cover = "http://thegamesdb.net/banners/" + GetDetailscover(TheGameDBxml_byid,system,)
        game_genre = GetDetailsgenre(TheGameDBxml_byid)
        db_path = os.path.join(os.path.abspath(""),"Gamez.db")
        connection = sqlite3.connect(db_path)
        LogEvent("Adding " + system + "Game [ " + xmlGameTitle.replace("'","''") + " ] to Game List. Cover :" + game_cover.replace("'","''"))
        if(xmlGameTitle <> ''):
            sql = "INSERT INTO games (game_name,game_type,system,cover) values('" + xmlGameTitle.replace("'","''") + "','" + game_genre + "','" + system + "','" + game_cover + "')"
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            tagnbr = tagnbr + 1
      
def GetDetailsgenre(TheGameDBurl):
    try:
        xmlTaggenre = TheGameDBurl.getElementsByTagName('genre')[0].toxml()
        xmlGamegenre=xmlTaggenre.replace('<genre>','').replace('</genre>','')
        LogEvent("Found a Genre: " + xmlGamegenre)
        return str(xmlGamegenre)
    except:
        xmlGamegenre="Game"
        return xmlGamegenre


def GetDetailscover(TheGameDBurl,system):
    try:
        xmlTagcover = TheGameDBurl.getElementsByTagName('boxart')[0].toxml()  
        #coverside=xmlTagcover.getAttribute('side')
        xmlGamecover=xmlTagcover.replace('<boxart (.*)>','').replace('</boxart>','')    
        LogEvent("Found a Cover: " + xmlGamecover)
        return str(xmlGamecover)
    except:
        if(system == "PS3"):
            xmlGamecover="_platformviewcache/platform/boxart/12-1.jpg"
        elif(system == "PC"):
            xmlGamecover="_platformviewcache/platform/boxart/1-1.jpg"
        else:
            xmlGamecover="None"
        return str(xmlGamecover)

def GetXmlFromTheGameDB(term,system,TheGameDB_id):
    #gamefile = None
    #gamedata = None
    if(system == 'PS3'):
       Platform = "Sony+Playstation+3"
    elif(system == 'PC'):
       Platform = "PC"
    elif(system == 'Wii'):
       Platform = "Nintendo+Wii"
    elif(system == 'Xbox360'):
       Platform = "Microsoft+Xbox+360"
    try:
       if(TheGameDB_id != "fake"):
           gamefile = urllib2.urlopen('http://thegamesdb.net/api/GetGame.php?id=' + TheGameDB_id)
           LogEvent('Search for [ "' + term + '" ] http://thegamesdb.net/api/GetGame.php?id=' + TheGameDB_id)
       else:
           gamefile = urllib2.urlopen('http://thegamesdb.net/api/GetGame.php?name=' + term.replace(' ','+') + '&platform=' + Platform)
           LogEvent( 'Search for [ "' + term + '" ] http://thegamesdb.net/api/GetGame.php?name=' + term.replace(' ','+') + '&platform=' + Platform)
       gamedata = gamefile.read()
       gamefile.close()
       dom = parseString(gamedata)    		
       return dom
    except:
        LogEvent("ERROR: I can not get any Data from TheGameDB.org")