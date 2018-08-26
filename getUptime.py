#import libraries
import telnetlib
import socket
import errno
from subprocess import check_output, CalledProcessError
import urllib2
import re
from datetime import datetime,timedelta
import sqlite3 as lite
import plotly
import platform
import ConfigParser
import os
import platform
import logging

def readConfig():
    if os.path.isfile(settingsFilename):
        config = ConfigParser.ConfigParser()
        config.read(settingsFilename)
        configDict = {}
        for section in config.sections():
            for(key,value) in config.items(section):
                configDict[key] = value
        # check if every read parameter is ok
        validatedConfigDict = validateConf(configDict)
    else:
        createExampleFile()
        validatedConfigDict = None
    return validatedConfigDict

def createExampleFile():
    exampleFile = open(settingsFilename,"w")
    filecontent = "[network]\nip = 192.168.1.254\nport = 23\nwirelessconnection = 1\n"
    filecontent = filecontent + "myssid = ssid\n[login]\nusername = Administrator\n"
    filecontent = filecontent + "password = password\n[plotly]\nonlinePlot = 0\n"
    filecontent = filecontent + "plotlyusername = username\nplotlyapikey = exampleapikey\n"
    filecontent = filecontent + "[dbname]\nDBfilename = DSLuptime.db"

    exampleFile.write(filecontent)

def validateConf(configDict):
    exc = ""

    try:
        #check if there's an empty parameter
        for key in configDict:
            if configDict[key] == '':
                exc = "Evaluation error: Empty " + key + " parameter"
                raise Exception

        #ip address evaluation
        socket.inet_aton(configDict['ip'])

        #port number evaluation (default telnet port number is 23)
        if(not configDict['port'].isdigit() or
           (int(configDict['port']) <= 0 or 
            int(configDict['port']) > 65536)):
            exc = "Evaluation error: Invalid port number"
            raise Exception
        
        #wirelessconnection evaluation
        if(configDict['iswirelessconnection'] != '0' and
           configDict['iswirelessconnection'] != '1'):
           exc = "Evaluation error: Invalid iswirelessconnection option, please set it to 0 or 1"
           raise Exception

        #plot option evaluation
        if(configDict['onlineplot'] != '0' and 
           configDict['onlineplot'] != '1'):
           exc = "Evaluation error: Invalid onlineplot option, please set it to 0 or 1"
           raise Exception
        
    #invalid ip address
    except socket.error:
        writeErrorLog("Evaluation error: Invalid IP address")
        configDict = None
    #Generic exception
    except Exception:
        writeErrorLog(exc)
        configDict = None
    return configDict

def writeErrorLog(errorString):    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.error(" "+ now+ " - " + errorString)

#function to check if there's an internet connection available
def checkInternetConnection():
    try:
        urllib2.urlopen('http://www.google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        writeErrorLog("urllib2.URLError")
        return False

#function to extract the SSID that my PC is connected to
def extractSSID():
    obtainedSSID = "WiFi not found"
    if platform.system() == "Linux":
        try:
            scanoutput = check_output("iwgetid")
            line = scanoutput.split('ESSID:"')
            #delete 2 characters because there's a " and a \n at the end of line
            obtainedSSID = line[1][:-2]
        except CalledProcessError as e:
            writeErrorLog("Exception caught: CalledProcessError")
    elif platform.system() == "Windows":
        scanoutput = check_output("netsh wlan show interfaces")
        for line in scanoutput.splitlines():
            if line[4:8] == "SSID":
                obtainedSSID = line[29:]
    else:
        obtainedSSID = "Not Linux or Windows"
    return obtainedSSID

#function to convert the string "X giorno/i HH:MM:SS" to minutes
def fromDaysToMinutes(daysHoursMinutes):
    if("giorno" in daysHoursMinutes):
        days, separator, time = daysHoursMinutes.partition(' giorno, ')
    else:
        days, separator, time = daysHoursMinutes.partition(' giorni, ')
    
    dt = datetime.strptime(time[:-3], '%H:%M')
    hours = int(dt.hour)
    minutes = int(dt.minute)
    
    # sum and convert days and hours to minutes
    totalMinutes = (int(days) * 24 * 60) + (hours * 60) + minutes
    return totalMinutes

#function to format data from dd/mm/YYYY to YYYY/mm/dd 
def formatDate(notFormattedDate):
    return datetime.strptime(notFormattedDate, '%d/%m/%Y').strftime('%Y-%m-%d')

def calcReconnection(eventDate,uptime):
    datetimet = datetime.strptime(eventDate, '%Y-%m-%d %H:%M')
    calculatedDatetime = datetimet - timedelta(minutes=uptime)
    return calculatedDatetime

#function to insert data to database DBFilename
def insertDataToDBandCreateChart(collectedData):
    con = None
    periodList = []
    datetimeList = []
    try:
        con = lite.connect(DBFilename)
        with con:
            cur = con.cursor()
            # create table if not exists
            cur.execute("CREATE TABLE IF NOT EXISTS DSLuptime (eventID integer NOT NULL PRIMARY KEY,eventDate DATETIME NOT NULL,eventDuration INTEGER NOT NULL, reconnectionDatetime DATETIME NOT NULL);")
            # insert data
            cur.executemany("INSERT INTO DSLuptime (eventDate, eventDuration, reconnectionDatetime) VALUES (?,?,?);",(collectedData))
            
            cur.execute("SELECT reconnectionDatetime FROM DSLuptime")
            row = ""
            diffReconn = datetime.strptime("1970-01-01 00:00:00","%Y-%m-%d %H:%M:%S")
            while (row != None):
                row = cur.fetchone()
                if row != None:
                    currentRow = datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S")
                    #if reconnection date of the current row is different from the previous one, then...
                    if(currentRow != diffReconn):
                        #if the previous row is different from a dummy value (1970...), then acquire period:
                        # period = currentrow (datetime) - previous row (datetime)
                        if(diffReconn != (datetime.strptime("1970-01-01 00:00:00","%Y-%m-%d %H:%M:%S"))):
                            period = currentRow - diffReconn
                        #if the previous row is equal to a dummy value, then period = 0
                        else:
                            period = timedelta(seconds=0)
                        #calculate n. of minutes of the period
                        periodMinutes = period.seconds / 60 + period.days * 24 * 60
                        #sometimes periods are not exact, this is to avoid invalid periods
                        if (periodMinutes > 1):
                            periodList.append(periodMinutes)
                            #append to datetimeList the two dates of the period
                            datetimeList.append("from %s to %s"%(diffReconn,currentRow))
                        #update the previous row with the current one
                        diffReconn = currentRow
            if ((periodList) and (datetimeList)):
                #delete from list the first element because it's 0 (it's calculated with the dummy date)
                periodList.pop(0)
                #delete from list the first element because it from the dummy date to the first one, useless
                datetimeList.pop(0)
                #create data
                data = [plotly.graph_objs.Bar(x=datetimeList, y=periodList,name='Minutes')]
                #create layout with legend activated
                layout = plotly.graph_objs.Layout(showlegend=True)
                #create figure
                fig = plotly.graph_objs.Figure(data=data, layout=layout)

                if(onlinePlot == True):
                    '''
                    online plot: in order to use it you must signup on plot.ly website and configure it
                    by using the following commands in python cli:
                    >>> import plotly
                    >>> plotly.tools.set_credentials_file(username='DemoAccount', api_key='lr1c37zw81')
                    more info here: https://plot.ly/python/getting-started/#initialization-for-online-plotting
                    '''
                    plotly.tools.set_credentials_file(username=plotlyUsername, api_key=plotlyAPIkey)
                    plotly.plotly.plot(fig, filename="DSL uptime chart", auto_open=False)
                else:
                    #offline plot
                    plotly.offline.plot(fig, filename="DSL uptime chart.html", auto_open=False)
            else:
                writeErrorLog("Nothing to plot")

    except lite.Error, e:
        writeErrorLog("sqlite3.Error: %s" %e.args[0])
    finally:
        if con:
            con.close()

def getTelnetData():
    try:
        #declaration, initialization and beginning of telnet communication
        tn = telnetlib.Telnet(config['ip'], config['port'])
        #read until it finds "Username : "
        tn.read_until("Username : ")
        #write username + \r (carriage return)
        tn.write(username + "\r")
        tn.read_until("Password : ")
        tn.write(password + "\r")
        tn.write("system settime\r")
        tn.write("xdsl info\r")
        tn.write("exit\r")
        #store the telnet output into output variable
        output = tn.read_all()
        tn.close()
    except socket.error, v:
        errorcode=v[0]
        if errorcode==errno.ECONNREFUSED:
            writeErrorLog("socket.error: connection refused")

    return output

#main function
def main():
    collectedData = []
    #just comment out the second if, if there's no need to check ssid (e.g. wired connection)
    #if(checkInternetConnection() & ((extractSSID() == mySSID) or extractSSID() == "Not Linux or Windows")):
    if(checkInternetConnection() & 
      (((isWirelessConnection) & (extractSSID() == mySSID or extractSSID() == "Not Linux or Windows")) or 
      not isWirelessConnection)):
        output = getTelnetData()

        date = ""
        time = ""
        #parse output to find the desired lines
        for line in output.splitlines():
            uptime = -1
            if(re.match(r"date = [0-9]{2,2}/[0-9]{2,2}/[0-9]{4,4}", line)):
                date = formatDate(line[7:])
            elif(re.match(r"time = [0-9]{2,2}:[0-9]{2,2}:[0-9]{2,2}", line)):
                time = line[7:-3]
            elif(re.search(r":\s+ [0-9]+ giorno?i?,\s[0-9]{0,2}:[0-9]{2,2}:[0-9]{2,2}",line)):
                uptime = fromDaysToMinutes(line[33:])
            
            #if every desired data is collected we can proceed
            if((date != "") and
                (time != "") and
                (uptime != -1)):
                eventDatetime = date + " " + time
                reconnectionDatetime = calcReconnection(eventDatetime,uptime)
                #insertion of data to a list of tuples, then it's passed to insertDataToDBandCreateChart() function
                collectedData.append([eventDatetime, uptime, reconnectionDatetime])
                insertDataToDBandCreateChart(collectedData)
    else:
        writeErrorLog("Not connected to your home network or no network connection available")


#global variables
settingsFilename = "settings.conf"
logging.basicConfig(format='%(levelname)s:%(message)s',filename='output.log',level=logging.ERROR)

config = readConfig()
if config != None:
    try:
        ip = config['ip']
        port = config['port']
        username = config['username']
        password = config['password']
        isWirelessConnection = config['iswirelessconnection']
        if (isWirelessConnection == '1'):
            isWirelessConnection = True
            #used to check if I'm connected to my home network
            mySSID = config['myssid']
        else:
            isWirelessConnection = False
            mySSID = None
        onlinePlot = config['onlineplot']
        if(onlinePlot == '1'):
            onlinePlot = True
        else:
            onlinePlot = False
        
        plotlyUsername = config['plotlyusername']
        plotlyAPIkey = config['plotlyapikey']
        DBFilename = config['dbfilename']
    except KeyError as e:
        writeErrorLog('Missing config line')
else:
    writeErrorLog("Invalid settings.conf file or exception caught")

#use of functions
main()
