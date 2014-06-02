import os
import sys
import re
import urllib
import urllib2
import requests
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

    def FindGames(self, manualSearchGame,nzbmatrixusername, nzbmatrixapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbMatrixEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,isTorrentTPBEnabled,torrentBlackholePath,isNZBSU,nzbsuapi,retention):
        # First some variables
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        isPS3TBEnable = config.get('SystemGenerated','ps3_tb_enable').replace('"','')
        isPS3JBEnable = config.get('SystemGenerated','ps3_jb_enable').replace('"','')       
        BlacklistWordsXbox360 = config.get('SystemGenerated','blacklist_words_xbox360').replace('"','')
        BlacklistWordsWii = config.get('SystemGenerated','blacklist_words_wii').replace('"','')
        BlacklistWordsPS3 = config.get('SystemGenerated','blacklist_words_ps3').replace('"','')
        blacklistwords = ''
        if(isSabEnabled == "1"):       
            GameTasks().CheckIfPostProcessExistsInSab(sabnzbdApi,sabnzbdHost,sabnzbdPort)
        nzbmatrixusername = nzbmatrixusername.replace('"','')
        nzbmatrixapi = nzbmatrixapi.replace('"','')
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
                     blacklistwords = BlacklistWordsPS3
                     if(isPS3TBEnable == "1"):
                        blacklistwords = "TB"
                        DebugLogEvent("[PS3] execlude True Blue") 
                     if(isPS3JBEnable == "1"):
                        blacklistwords = "JB"
                        DebugLogEvent("[PS3] execlude Jail Break")
                blacklistwords = re.split(';|,',blacklistwords.replace(" ", ""))
                     		  
                if(isNzbMatrixEnabled == "1"):
                    DebugLogEvent("Matrix Enable")
                    if(nzbmatrixusername <> '' and nzbmatrixapi <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on NZB Matrix")
                            isDownloaded = GameTasks().FindGameOnNZBMatrix(game_name,game_id,nzbmatrixusername,nzbmatrixapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention)
                    else:
                        LogEvent("NZB Matrix Settings Incomplete.")
                
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
                     DebugLogEvent("TorrentBlackHole Enable")
                     if(isTorrentKATEnabled == "1"):
                          LogEvent("KAT Enabled")
                          if(isDownloaded is None or isDownloaded == False):
                               LogEvent("Checking for game [" + game_name + "] on KickAss Torrents")
                               isDownloaded = GameTasks().FindGameOnKAT(game_id,game_name,system,torrentBlackholePath,blacklistwords)
                               LogEvent("Done checking for game [" + game_name + "] on KickAss Torrents")
                               print isDownloaded
                     if(isTorrentTPBEnabled == "1"):
                          LogEvent("TPB Enabled")
                          if(isDownloaded is None or isDownloaded == False):
                               LogEvent("Checking for game [" + game_name + "] on ThePirateBay.se")
                               isDownloaded = GameTasks().FindGameOnTPB(game_id,game_name,system,torrentBlackholePath,blacklistwords)
                               LogEvent("Done checking for game [" + game_name + "] on ThePirateBay.se")
                          else:
                               print isDownloaded
            except:
                continue
        return

    def FindGameOnNZBMatrix(self,game_name,game_id,username,api,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention):
        catToUse = ""
        if(system == "Wii"):
            catToUse = "44"
        elif(system == "Xbox360"):
            catToUse = "14"
        elif(system == "PS3"):
            catToUse = "43"
        elif(system == "PC"):
            catToUse = "10"
        else:
            LogEvent("Unrecognized System")
            return False
        searchname = replace_all(game_name)
        url = "http://api.nzbmatrix.com/v1.1/search.php?search=" + searchname + "&num=1&maxage=" + retention + "&catid=" + catToUse + "&username=" + username + "&apikey=" + api
        DebugLogEvent("Search URL [ " + url + " ]")
        try:
            opener = CostumOpener()
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
        except Exception, e:
            LogEvent("Unable to connect to NZBMatrix Server: %s \n Exeption: %s" % (url, e))
            return False
        try:
            responseData = response.split("\n")
            fieldData = responseData[0].split(":")
            nzbID = fieldData[1]
            DebugLogEvent("NZB_ID:" + str(nzbID))
            nzbID = nzbID.replace(";","")
            
            if(nzbID <> "nothing_found" and nzbID <> "API_RATE_LIMIT_REACHED"):
                
                try:
                    fieldDataName = responseData[1].split(":")
                    nzbName = fieldDataName[1]
                    nzbName = nzbName.replace(";","")
                    AdditionWords(nzbName,game_id)
                except:
                    DebugLogEvent("Something went wrong with getting addition")

                LogEvent("Game found on NZB Matrix")
                nzbUrl = "http://api.nzbmatrix.com/v1.1/download.php?id=" + nzbID + "&username=" + username + "&apikey=" + api
                result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                if(result):
                    UpdateStatus(game_id,"Snatched")
                    return True

            elif(nzbID == "nothing_found"):
                LogEvent("Nothing found on NZBMatrix.com")
            elif(nzbID == "API_RATE_LIMIT_REACHED"):
                LogEvent("NZBMatrix return: API RATE LIMIT REACHED")
            elif(nzbID == "invalid_login"):
                LgeEvent("NZBMatrix return: Invalid login")
            return False
        except:
            LogEvent("Error getting game [" + game_name + "] from NZB Matrix")
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
        url = "http://nzb.su/api?apikey=" + api + "&t=search&maxage=" + retention + "&cat=" + catToUse + "&q=" + searchname.replace(" ","+")
        DebugLogEvent("Serach URL [" + url + "]") 
        try:
            data = urllib2.urlopen(url, timeout=20).read()
        except:
            LogEvent("Unable to connect to Newznab Server: " + url)
            return False
        try:           
            d = feedparser.parse(data)
            for item in d.entries:
                LogEvent("Game found on http://nzb.su")
                nzbTitle = item.title
                for blacklistword in blacklistwords:
                    if(blacklistword == ''):
                        DebugLogEvent("No blacklisted word(s) are given")
                    else:
                        DebugLogEvent(" The Word is " + str(blacklistword))
                    if not str(blacklistword) in nzbTitle or blacklistword == '':
                          AdditionWords(nzbTitle,game_id)
                          LogEvent("Game found on http://nzb.su")
                          nzbUrl = item.link
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
        nzbUrl = urllib.quote(nzbUrl)
        url = "http://" + sabnzbdHost + ":" +  sabnzbdPort + "/sabnzbd/api?mode=addurl&pp=3&apikey=" + sabnzbdApi + "&name=" + nzbUrl + "&nzbname=" + game_name + " ("+ system + ")"
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
    	url = "http://www.kickass.to/json.php?q=" + game_name
        LogEvent("Searching KAT! Url=" + url)
    	try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
            jsonObject = json.loads(response)
            listObject = jsonObject['list']
            for record in sorted(listObject, key=lambda a: a['seeds'], reverse=True):
                title = record['title']
                torrentLink = record['torrentLink']
                category = record['category']
                if(category == "Games"):
                    if system.lower() in title.lower():
                        BlackListedWordsexist=GameTasks().CheckBlackListedWords(system,title,blacklistwords)
                        if(BlackListedWordsexist is False):
                            result = GameTasks().DownloadTorrent(torrentLink,title,torrentBlackholePath)
                            if(result == True):
                                UpdateStatus(game_id,"Snatched")
                                return result
        except:
            LogEvent("Unable to connect to KickAss Torrents")  
            return

    def FindGameOnTPB(self,game_id,game_name,system,torrentBlackholePath,blacklistwords):
        LogEvent("Pretending to search TPB, really KAT")
    	url = "http://www.kickass.to/json.php?q=" + game_name
    	try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
            jsonObject = json.loads(response)
            listObject = jsonObject['list']
            for record in sorted(listObject, key=lambda a: a['seeds'], reverse=True):
                title = record['title']
                torrentLink = record['torrentLink']
                category = record['category']
                if(category == "Games"):
                    if system.lower() in title.lower():
                        BlackListedWordsexist=GameTasks().CheckBlackListedWords(system,title,blacklistwords)
                        if(BlackListedWordsexist is False):
                            result = GameTasks().DownloadTorrent(torrentLink,title,torrentBlackholePath)
                            if(result == True):
                                UpdateStatus(game_id,"Snatched")
                                return result
        except:
            LogEvent("Unable to connect to KickAss Torrents")  
            return
    	
    def DownloadTorrent(self,torrentUrl,title,torrentBlackholePath):
    	try:
    	    LogEvent("Starting to get torrent")
            destdir = os.path.normpath(torrentBlackholePath) + os.sep
            legaltitle = GameTasks().LegalizeTitle(str(title))
    	    dest = destdir + legaltitle + ".torrent"
    	    r = requests.get(torrentUrl)
            with open(dest, "wb") as code:
                code.write(r.content)
    	    LogEvent("Torrent Added To Blackhole")
        except NameError as e:
            print e
    	except:
            print "Unexpected error:", sys.exc_info()[0]
    	    LogEvent("Unable to download torrent to blackhole: " + url)
            return False
    	return True

    def LegalizeTitle(self,title):
        replaces = [(c, '_') for c in title if not c.isalnum() and not c in ["_", "-", ".", "[", "]", "(", ")"]]
        newtitle = title
        for r in replaces:
            newtitle = newtitle.replace(r[0], r[1])
        return newtitle

    def CheckBlackListedWords(self,system,title,blacklistwords):
        if(blacklistwords<>""):
            for badword in (blacklistwords):
                if (len(badword) == 0):
                    continue
                if(badword.lower() in title.lower()):
                    LogEvent("found bad word " + badword.lower() + " in " + title.lower())
                    return True
            return False
        return False

    def CheckIfPostProcessExistsInSab(self,sabnzbdApi,sabnzbdHost,sabnzbdPort):
        
        path = os.path.join(gamez.PROGDIR, "postprocess")
        srcPath = os.path.join(path,"gamezPostProcess.py")
        url = "http://" + sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=get_config&apikey=" + sabnzbdApi + "&section=misc&keyword=script_dir"
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
        nzbMatrixUser = config.get('NZBMatrix','username').replace('"','')
        nzbMatrixApi = config.get('NZBMatrix','api_key').replace('"','')
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
        isNzbMatrixEnabled = config.get('SystemGenerated','nzbmatrix_enabled').replace('"','')
        isNewznabEnabled = config.get('SystemGenerated','newznab_enabled').replace('"','')
        isnzbsuEnable = config.get('SystemGenerated','nzbsu_enabled').replace('"','')
        isNzbBlackholeEnabled = config.get('SystemGenerated','blackhole_nzb_enabled').replace('"','')
        nzbBlackholePath = config.get('Blackhole','nzb_blackhole_path').replace('"','')
        isTorrentBlackholeEnabled = config.get('SystemGenerated','blackhole_torrent_enabled').replace('"','')
        isTorrentKATEnabled = config.get('SystemGenerated','torrent_kat_enabled').replace('"','')
        isTorrentTPBEnabled = config.get('SystemGenerated','torrent_tpb_enabled').replace('"','')
        torrentBlackholePath  = config.get('Blackhole','torrent_blackhole_path').replace('"','')
        retention = config.get('SystemGenerated','retention').replace('"','')
        manualSearchGame = dbid
        LogEvent("Searching for games")
        GameTasks().FindGames(manualSearchGame,nzbMatrixUser,nzbMatrixApi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbMatrixEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,isTorrentTPBEnabled,torrentBlackholePath,isnzbsuEnable,nzbsuapi,retention)
            

