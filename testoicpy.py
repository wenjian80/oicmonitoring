# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 14:22:09 2021

@author: bjlim
"""

import json
import time
import datetime
import requests
import csv
#import cx_Oracle

#Set headers, witht he authroization. us epostman to get the Authorization
my_headers  = {"Content-Type": "application/json", "Authorization": "Basic changeit", "X-HTTP-Method-Override": "PATCH"}


#Filter by 6h based on which integration you want to filter
response = requests.get("https://changeit/ic/api/integration/v1/monitoring/instances?q={timewindow:'6h', code:'TESTTHAIOIC'}", headers=my_headers)

responseJson = response.json()

instanceIdList = responseJson['items']
instanceArray= []

for list in instanceIdList:    
    instanceArray.append(list['id'])


#Get each instance details    
i = 0
datetimeFormat = '%a %b %d %H:%M:%S.%f %p %Z %Y'
previous_date_time_str=""
totalTimeTaken=0
printArray = []

#write csv header
with open('timetaken.csv','a') as fd:            
    fd.write("Instance Id|Total Time taken(millseconds)|Timestamp|Message|Time  Taken" + "\n")

#Open connection to json db in cloud
#Refer to https://www.oracle.com/database/technologies/appdev/python/quickstartpython.html#copy
#CREATE TABLE "ADMIN"."ACTIVITY_STREAM" 
#   (	"INSTANCE_ID" NUMBER(*,0), 
#	"TOTAL_TIME_TAKEN" NUMBER(*,0), 
#	"TIMESTAMP" VARCHAR2(200 BYTE) COLLATE "USING_NLS_COMP", 
#	"MESSAGE" CLOB COLLATE "USING_NLS_COMP", 
#	"TIME_TAKEN" NUMBER(*,0)
#   )
#CREATE TABLE "ADMIN"."INSTANCE_PAYLOAD" 
#   (	"INSTANCE_ID" NUMBER(*,0), 
#	"PAYLOAD" CLOB COLLATE "USING_NLS_COMP",
#    "TOTAL_TIME_TAKEN" NUMBER(*,0)
#   )
#alter table INSTANCE_PAYLOAD add constraint "ENSURE_JSON" check (PAYLOAD is json) enable
#cx_Oracle.init_oracle_client(lib_dir=r"D:\instantclient_19_10")
#connection = cx_Oracle.connect(user="ADMIN", password="Welc0me1234#", dsn="jsdondb_tpurgent")
#cursor = connection.cursor()

insertInstance = ('insert into INSTANCE_PAYLOAD '
        'values(:vinstanceId,:vPayload, :vTimetaken)')

insertSql = ('insert into ACTIVITY_STREAM '
        'values(:vinstanceId,:vTotalTimeTaken,:vTimestamp,:vMessage, :vTimetaken)')

updateSql = ('update ACTIVITY_STREAM set TOTAL_TIME_TAKEN=:vTotalTimeTaken where INSTANCE_ID=:vinstanceId')

                
for instance in instanceArray:    
    url = "https://changeit/ic/api/integration/v1/monitoring/instances/" + instance + "/activityStream"
    response = requests.get(url, headers=my_headers)        
    data = response.json()
    mylists = data['ascList']
    #ischild=true is an internal timing pull from logs whereby lgos where be gone to caculate each internal steps
    #So w eonly take isChild=false which is from databsae.	
    for list in mylists:         
        if (list['isChild'] == False) :                    
            date_time_str = list['timestamp']    
            
            if (i ==0) :    
                printArray.append(list['timestamp'] + "|" + list['message'].strip('\n').replace('\n', '') + "|0")
#                cursor.execute(insertSql, [instance, 0, list['timestamp'], list['message'].strip('\n').replace('\n', ''), 0])
            else :        
                diff = datetime.datetime.strptime(date_time_str, datetimeFormat)\
                       - datetime.datetime.strptime(previous_date_time_str, datetimeFormat)
                diffInMillSeconds = diff.microseconds/1000
                totalTimeTaken = diffInMillSeconds + totalTimeTaken
                printArray.append(list['timestamp'] + "|" + list['message'].strip('\n').replace('\n', '') + "|" + str(diffInMillSeconds))
#                cursor.execute(insertSql, [instance, 0, list['timestamp'], list['message'].strip('\n').replace('\n', ''), str(diffInMillSeconds)])
           
            i = i + 1
            previous_date_time_str = date_time_str
    

    for row in printArray:            
        with open('timetaken.csv','a') as fd:            
            fd.write(instance + "|" + str(totalTimeTaken) + "|" + row + "\n")            
    
#    cursor.execute(insertInstance, [instance, str(data), str(totalTimeTaken)])    
#    cursor.execute(updateSql,[str(totalTimeTaken), instance])
    
    totalTimeTaken=0
    i = 0
    printArray = []

#connection.commit()