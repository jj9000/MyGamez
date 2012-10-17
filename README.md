<hr />

Gamez is currently in *Alpha* release. There may be bugs in the application.

Gamez is an automated downloader for video games. The user adds the games they wish to download and Gamez will attempt to find the game and download it.

As of the current release, only Wii, Xbox360, PS3 and PC games are supported. 

Current Features:

    * Local database of all Wii and Xbox360 games
    * Grep gamedata from TheGamesDB.net
    * Automatically sends NZB's to Sabnzbd
    * Support for NZBMatrix, Newznab and nzb.su
    * Torrents with "black hole" function
    * API

<hr />

***Dependencies***

Gamez requires Python and CherryPY. The CherryPy module is included with Gamez. Python 2.7 or higher must be installed on the system on which Gamez will be ran.
For https support you also need openssl for creating the certificate.

<hr />

***Options***

Gamez has some console options:
     
      *  -d,         --daemonize         Run the server as a daemon
      *  -D,         --debug             Enable Debug Log
      *  -p PIDFILE, --pidfile=PIDFILE   Store the process id in the given file
      *  -P PORT,    --port=PORT         Force webinterface to listen on this port
      *  -n,         --nolaunch          Don't start browser
      *  -b DATADIR, --datadir=DATADIR   Set the directory for the database
      *  -c CONFIG,  --config=CONFIG     Path to configfile

<hr />