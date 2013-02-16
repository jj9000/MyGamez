import os
import sys
import re
import urllib
import urllib2
import shutil
import stat
import json
import ConfigParser
from xml.dom.minidom import *

import gamez

from DBFunctions import GetRequestedGamesAsArray,UpdateStatus,AdditionWords
from Helper import replace_all,FindAddition
from subprocess import call
from Logger import LogEvent,DebugLogEvent
from Constants import VersionNumber
import lib.feedparser as feedparser



class CostumOpener(urllib.FancyURLopener):
    version = 'Gamez/' + VersionNumber()



class GameTasks():

    def FindGames(self, manualSearchGame,nzbsrususername, nzbsrusapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isnzbsrusEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,torrentBlackholePath,isNZBSU,nzbsuapi,retention):
        # First some variables
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        isPS3TBEnable = config.get('SystemGenerated','ps3_tb_enable').replace('"','')
        isPS3JBEnable = config.get('SystemGenerated','ps3_jb_enable').replace('"','')       
        BlacklistWordsXbox360 = config.get('SystemGenerated','blacklist_words_xbox360').replace('"','')
        BlacklistWordsWii = config.get('SystemGenerated','blacklist_words_wii').replace('"','')
        blacklistwords = ''
        if(isSabEnabled == "1"):       
            GameTasks().CheckIfPostProcessExistsInSab(sabnzbdApi,sabnzbdHost,sabnzbdPort)
        nzbsrususername = nzbsrususername.replace('"','')
        nzbsrusapi = nzbsrusapi.replace('"','')
        newznabApi = newznabApi.replace('"','')     
        newznabWiiCat = newznabWiiCat.replace('"','')  
        games = GetRequestedGamesAsArray(manualSearchGame)
        for game in games:
            try:
                game_name = str(game[0])
                game_id = str(game[1])
                system = str(game[2])
                LogEvent("Searching for game: " + game_name)
                isDownloaded = False
                if(system == "Xbox360" and BlacklistWordsXbox360 <> ''):
                     blacklistwords = BlacklistWordsXbox360
                     DebugLogEvent("Blacklisted Words for XBOX360 [ " + str(blacklistwords) + " ]")
                if(system == "Wii" and BlacklistWordsWii <> ''):
                     blacklistwords = BlacklistWordsWii
                     DebugLogEvent("Blacklisted Words for Wii [ " + blacklistwords + " ]")
                if(system == "PS3"):
                     if(isPS3TBEnable == "1"):
                        blacklistwords = "TB"
                        DebugLogEvent("[PS3] execlude True Blue") 
                     if(isPS3JBEnable == "1"):
                        blacklistwords = "JB"
                        DebugLogEvent("[PS3] execlude Jail Break")
                blacklistwords = re.split(';|,',blacklistwords)
                     		  
                if(isnzbsrusEnabled == "1"):
                    DebugLogEvent("Matrix Enable")
                    if(nzbsrususername <> '' and nzbsrusapi <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on NZB Matrix")
                            isDownloaded = GameTasks().FindGameOnNzbsrus(game_name,game_id,nzbsrususername,nzbsrusapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention)
                    else:
                        LogEvent("NZBSRus Settings Incomplete.")
                
                if(isNewznabEnabled == "1"):
                    DebugLogEvent("Newznab Enable")
                    if(newznabWiiCat <> '' and newznabXbox360Cat <> '' and newznabPS3Cat <> '' and newznabPCCat <> '' and newznabApi <> '' and newznabHost <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] for ["+ system + "] on Newznab")
                            isDownloaded = GameTasks().FindGameOnNewznabServer(game_name,game_id,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,system,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention)
                    else:
                        LogEvent("Newznab Settings Incomplete.")  
                        
                if(isNZBSU == "1"):
                    DebugLogEvent("nzb.su Enable")
                    if(nzbsuapi <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on nzb.su")
                            isDownloaded = GameTasks().FindGameOnNZBSU(game_name,game_id,nzbsuapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention)
                    else:
                        LogEvent("NZBSU Settings Incomplete.")

                if(isTorrentBlackholeEnabled == "1"):
                     DebugLogEvent("Torrent Enable")
                     if(isTorrentKATEnabled == "1"):
                		if(isDownloaded == False):
                		    LogEvent("Checking for game [" + game_name + "] on KickAss Torrents")
                		    isDownloaded = GameTasks().FindGameOnKAT(game_id,game_name,system,torrentBlackholePath,blacklistwords)
            except:
                continue
        return

    def FindGameOnNzbsrus(self,game_name,game_id,nzbsrus_uid,nzbsrus_api,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention):
        catToUse = ''
        if(system == "Wii"):
            catToUse = "92"
        elif(system == "Xbox360"):
            catToUse = "88"
        elif(system == "PS3"):
            catToUse = "89"
        elif(system == "PC"):
            catToUse = "27"		
        else:
            LogEvent("Unrecognized System")
            return False
        game_name = replace_all(game_name)
        url = "http://www.nzbsrus.com/api.php?key=" + nzbsrus_api + "&uid=" + nzbsrus_uid + "&cat=" + catToUse + "&searchtext=" + game_name.replace(" ","+")
        DebugLogEvent("Serach URL [" + url + "]") 
        try:
            opener = CostumOpener()
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
        except:
            LogEvent("Unable to connect to Nzbsrus.com")
            return False
        try:
            if(response == "[]"):
                return False            
            jsonObject = json.loads(response)['results']
            for item in jsonObject:
                nzbTitle = item["name"]
                nzbID = item["id"]                
                nzbKey = item["key"]
                nzbUrl ="http://www.nzbsrus.com/nzbdownload_rss.php/" + nzbID + "/" + nzbsrus_uid + "/" + nzbKey + "/"
                for blacklistword in blacklistwords:
                    if(blacklistword == ''):
                        DebugLogEvent("No blacklisted word(s) are given")
                    else:
                        DebugLogEvent(" The Word is " + str(blacklistword))
                    if not str(blacklistword) in nzbTitle or blacklistword == '':
                        gamenameaddition = FindAddition(nzbTitle)
                        DebugLogEvent("Additions for " + game_name + " are " + gamenameaddition)
                        game_name = game_name + gamenameaddition
                        LogEvent("Game found on NzbsRus")
                        result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                        if(result):
                            UpdateStatus(game_id,"Snatched")
                            return True
                        return False
                    else:
                        LogEvent('Nothing found without blacklistet Word(s) "' + str(blacklistword) + '"')
                        return False
        except:
            LogEvent("Error getting game [" + game_name + "] from NzbsRus")
            return False

    def FindGameOnNewznabServer(self,game_name,game_id,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,system,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention):
        catToUse = ''
        if(system == "Wii"):
            catToUse = newznabWiiCat
        elif(system == "Xbox360"):
            catToUse = newznabXbox360Cat
        elif(system == "PS3"):
            catToUse = newznabPS3Cat
            DebugLogEvent("System [ " + system + " ] and catToUse [ " + catToUse + " ] original Cat [" + newznabPS3Cat + "]") 
        elif(system == "PC"):
            catToUse = newznabPCCat		
            DebugLogEvent("PC: System [ " + system + " ] and catToUse [ " + catToUse + " ]")
        else:
            LogEvent("Unrecognized System")
            return False
        game_name = replace_all(game_name)
        searchname = replace_all(game_name)

        if not newznabHost.startswith('http'):
            newznabHost = "http://" + newznabHost
            LogEvent("!!!! Notice: Please update your Newznab settings and add http(s) to the adress  !!!!")

        if(newznabPort == '80' or newznabPort == ''):
            url = newznabHost + "/api?apikey=" + newznabApi + "&t=search&maxage=" + retention + "&cat=" + catToUse + "&q=" + searchname.replace(" ","+") + "&o=xml"
        else:
            url = newznabHost + ":" + newznabPort + "/api?apikey=" + newznabApi + "&t=search&maxage=" + retention + "&cat=" + catToUse + "&q=" + searchname.replace(" ","+") + "&o=xml"
        try:
            opener = urllib.FancyURLopener({})
            self.responseObject = opener.open(url)
            self.data = self.responseObject.read()
            self.responseObject.close()
            DebugLogEvent("Search for " + url)
        except:
            LogEvent("Unable to connect to Newznab Server: " + url)
            return False
        try:
            self.d = feedparser.parse(self.data)
            for item in self.d.entries:

                nzbTitle = item['title']
                nzbID = item['newznab_attr']['value']
                
                if(newznabPort == '80' or newznabPort == ''):
                   nzbUrl = newznabHost + "/api?apikey=" + newznabApi + "&t=get&id=" + nzbID
                else:
                   nzbUrl = newznabHost + ":" + newznabPort + "/api?apikey=" + newznabApi + "&t=get&id=" + nzbID  
                for blacklistword in blacklistwords:
                    if(blacklistword == ''):
                        DebugLogEvent("No blacklisted word(s) are given")
                    else:
                        DebugLogEvent(" The Word is " + str(blacklistword))
                    if not str(blacklistword) in nzbTitle or blacklistword == '':
                        DebugLogEvent("HERE WE ARE")
                        AdditionWords(nzbTitle,game_id)
                        LogEvent("Game found on Newznab")
                        result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                        if(result):
                            UpdateStatus(game_id,"Snatched")
                            return True
                        return False
                    else:
                        LogEvent('Nothing found without blacklistet Word(s) "' + str(blacklistword) + '"')
                        return False
        except:
            LogEvent("Error getting game [" + game_name + "] from Newznab")
            return False
            
    def FindGameOnNZBSU(self,game_name,game_id,api,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention):
        catToUse = ''
        if(system == "Wii"):
            catToUse = "1030"
        elif(system == "Xbox360"):
            catToUse = "1050"
        elif(system == "PS3"):
            catToUse = "1080"
        elif(system == "PC"):
            catToUse = "4050"		
        else:
            LogEvent("Unrecognized System")
            return False
        searchname = replace_all(game_name)
        url = "http://nzb.su/api?apikey=" + api + "&t=search&maxage=" + retention + "&cat=" + catToUse + "&q=" + searchname.replace(" ","+") + "&o=xml"
        DebugLogEvent("Serach URL [" + url + "]") 
        try:
            opener = urllib.FancyURLopener({})
            self.responseObject = opener.open(url)
            self.data = self.responseObject.read()
            self.responseObject.close()
            DebugLogEvent("Search for " + url)
        except:
            LogEvent("Unable to connect to Server: " + url)
            return False
        try:           
            for item in self.d.entries:

                nzbTitle = item['title']
                nzbID = item['newznab_attr']['value']

                for blacklistword in blacklistwords:
                    if(blacklistword == ''):
                        DebugLogEvent("No blacklisted word(s) are given")
                    else:
                        DebugLogEvent(" The Word is " + str(blacklistword))
                    if not str(blacklistword) in nzbTitle or blacklistword == '':
                          AdditionWords(nzbTitle,game_id)
                          LogEvent("Game found on http://nzb.su")
                          nzbUrl = "http://nzb.su/api?apikey=" + api + "&t=get&id=" + nzbID 
                          DebugLogEvent("Link URL [ " + nzbUrl + " ]")
                          result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                          if(result):
                              UpdateStatus(game_id,"Snatched")
                              return True
                          return False
                    else:
                        LogEvent('Nothing found without blacklistet Word(s) "' + str(blacklistword) + '"')
                        return False
        except:
            LogEvent("Error getting game [" + game_name + "] from http://nzb.su")
            return False


    def DownloadNZB(self,nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system):
        try:
            result = False
            if(isSabEnabled == "1"):
                result = GameTasks().AddNZBToSab(nzbUrl,game_name,system,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory)
            if(isNzbBlackholeEnabled == "1"):
            	result = GameTasks().AddNZBToBlackhole(nzbUrl,nzbBlackholePath,game_name,system)
            return result
        except:
            LogEvent("Unable to download NZB: " + url)
            return False

    def AddNZBToSab(self,nzbUrl,game_name,system,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory):

        if not sabnzbdHost.startswith('http'):
            sabnzbdHost = "http://" + sabnzbdHost
            LogEvent("!!!! Notice: Please update your sabnzbd settings and add http(s) to the adress !!!!")   

        nzbUrl = urllib.quote(nzbUrl)
        
        url = sabnzbdHost + ":" +  sabnzbdPort + "/sabnzbd/api?mode=addurl&pp=3&apikey=" + sabnzbdApi + "&name=" + nzbUrl + "&nzbname=" + game_name + " ("+ system + ")"
        if(sabnzbdCategory <> ''):
            url = url + "&cat=" + sabnzbdCategory
        DebugLogEvent("Send to sabnzdb: " + url) 
        try:
            responseObject = urllib.FancyURLopener({}).open(url)
            responseObject.read()
            responseObject.close()
        except:
            LogEvent("Unable to connect to Sanzbd: " + url)
            return False
        LogEvent("NZB added to Sabnzbd")
        return True
    
    def AddNZBToBlackhole(self,nzbUrl,nzbBlackholePath,game_name,system):
    	try:
    	    dest = nzbBlackholePath + game_name + " - " + system + ".nzb"
    	    LogEvent(nzbUrl)
    	    urllib.urlretrieve(nzbUrl,dest)
    	    LogEvent("NZB Added To Blackhole")
    	except:
    	    LogEvent("Unable to download NZB to blackhole: " + url)
            return False
    	return True
    	
    def FindGameOnKAT(self,game_id,game_name,system,torrentBlackholePath,blacklistwords):
    	url = "http://www.kickasstorrents.com/json.php?q=" + game_name
    	try:
	    opener = urllib.FancyURLopener({})
	    responseObject = opener.open(url)
	    response = responseObject.read()
            responseObject.close()
            jsonObject = json.loads(response)
            listObject = jsonObject['list']
            for record in listObject:
            	title = record['title']
                torrentLink = record['torrentLink']
                category = record['category']
                print category
                if(category == "Games"):
                    result = GameTasks().DownloadTorrent(torrentLink,title,torrentBlackholePath)
                    if(result == True):
                        UpdateStatus(game_id,"Snatched")
                        return result
        except:
            LogEvent("Unable to connect to KickAss Torrents")  
    	    return
    	
    def DownloadTorrent(self,torrentUrl,title,torrentBlackholePath):
    	try:
    	    dest = torrentBlackholePath + title + ".torrent"
    	    urllib.urlretrieve(torrentUrl,dest)
    	    LogEvent("Torrent Added To Blackhole")
    	except:
    	    LogEvent("Unable to download torrent to blackhole: " + url)
            return False
    	return True

    def CheckIfPostProcessExistsInSab(self,sabnzbdApi,sabnzbdHost,sabnzbdPort):
        
        path = os.path.join(gamez.PROGDIR, "postprocess")
        srcPath = os.path.join(path,"gamezPostProcess.py")
        url = sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=get_config&apikey=" + sabnzbdApi + "&section=misc&keyword=script_dir"
        try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
            if os.name == 'nt': 
                scriptDir = response.split(":")[2].replace(" '","")
                scriptDir = scriptDir + ":" + response.split(":")[3].replace("'","").replace(" ","").replace("{","").replace("}","").replace("\n","")
            else:
                scriptDir = response.split(":")[2].replace("'","").replace(" ","").replace("{","").replace("}","").replace("\n","")
            DebugLogEvent("Script Path :[" + scriptDir + "]")
            destPath = os.path.join(scriptDir,"gamezPostProcess.py")
            try:
                LogEvent("Copying post process script to Sabnzbd scripts folder")
                shutil.copyfile(srcPath,destPath)
            except:
                LogEvent("Unable to copy post process script to Sab folder")
                return
            try:
                LogEvent("Setting permissions on post process script")
                cmd = "chmod +x '" + destPath + "'"
                os.system(cmd)
            except:
                LogEvent("Unable to set permissions on post process script")
                return
        except:
            LogEvent("Unable to connect to Sanzbd: " + url)
            return
        return
    
    def CheckStatusInSab(self,game_name):
        
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        
        sabnzbdHost = config.get('Sabnzbd','host').replace('"','')
        sabnzbdPort = config.get('Sabnzbd','port').replace('"','')
        sabnzbdApi = config.get('Sabnzbd','api_key').replace('"','')        
        tagnbr = 0
        status = False
        url = "http://" + sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=history&apikey=" + sabnzbdApi + "&output=xml"
        
        DebugLogEvent("Checking for status of downloaded file in Sabnzbd")
        try:
            historyfile = urllib2.urlopen(url)
            sabnzbdhistorydata = historyfile.read()
            historyfile.close()
            history = parseString(sabnzbdhistorydata) 
            
            TagElements = history.getElementsByTagName("slot")
            for i in TagElements:
          
               historynameraw = history.getElementsByTagName('name')[tagnbr].toxml()
               historyname = historynameraw.replace('<name>','').replace('</name>','')
               if historyname == game_name:
                  historystatusraw = history.getElementsByTagName('status')[tagnbr].toxml()
                  historystatus = historystatusraw.replace('<status>','').replace('</status>','')
                  DebugLogEvent("Status for " + historyname + " is " + historystatus)
                  if(historystatus == 'Completed'):
                      status = True
                      break
                  else:
                      break
               else:
                 tagnbr += 1
                 continue
        except:
            DebugLogEvent("ERROR: Can not parse data from SABnzbd")
         
        return status

    def ForceSearch(self,dbid):
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        nzbsrusUser = config.get('nzbsrus','username').replace('"','')
        nzbsrusApi = config.get('nzbsrus','api_key').replace('"','')
        nzbsuapi = config.get('NZBSU','api_key').replace('"','')
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
        isnzbsrusEnabled = config.get('SystemGenerated','nzbsrus_enabled').replace('"','')
        isNewznabEnabled = config.get('SystemGenerated','newznab_enabled').replace('"','')
        isnzbsuEnable = config.get('SystemGenerated','nzbsu_enabled').replace('"','')
        isNzbBlackholeEnabled = config.get('SystemGenerated','blackhole_nzb_enabled').replace('"','')
        nzbBlackholePath = config.get('Blackhole','nzb_blackhole_path').replace('"','')
        isTorrentBlackholeEnabled = config.get('SystemGenerated','blackhole_torrent_enabled').replace('"','')
        isTorrentKATEnabled = config.get('SystemGenerated','torrent_kat_enabled').replace('"','')
        torrentBlackholePath  = config.get('Blackhole','torrent_blackhole_path').replace('"','')
        retention = config.get('SystemGenerated','retention').replace('"','')
        manualSearchGame = dbid
        LogEvent("Searching for games")
        GameTasks().FindGames(manualSearchGame,nzbsrusUser,nzbsrusApi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isnzbsrusEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,torrentBlackholePath,isnzbsuEnable,nzbsuapi,retention)
            

