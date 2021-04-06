# -*- coding: utf-8 -*-
"""
@author: bjlim
"""

import json
import time
import datetime
import requests
import csv

#Set headers, witht he authroization. us epostman to get the Authorization basic encryption
my_headers  = {"Content-Type": "application/json", "Authorization": "Basic keyinyoutown", "X-HTTP-Method-Override": "PATCH"}


#Filter by 6h based on which integration you want to filter
response = requests.get("https://youroicurl/ic/api/integration/v1/monitoring/instances?q={timewindow:'6h', code:'yourintegrationname'}", headers=my_headers)

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
	
for instance in instanceArray:    
    url = "https://youroicurl/ic/api/integration/v1/monitoring/instances/" + instance + "/activityStream"
    response = requests.get(url, headers=my_headers)        
    data = response.json()
    mylists = data['ascList']
    
    
    for list in mylists:        
        date_time_str = list['timestamp']    
        
        if (i ==0) :    
            printArray.append(list['timestamp'] + "|" + list['message'].strip('\n').replace('\n', '') + "|0")
        else :        
            diff = datetime.datetime.strptime(date_time_str, datetimeFormat)\
                   - datetime.datetime.strptime(previous_date_time_str, datetimeFormat)
            diffInMillSeconds = diff.microseconds/1000
            totalTimeTaken = diffInMillSeconds + totalTimeTaken
            printArray.append(list['timestamp'] + "|" + list['message'].strip('\n').replace('\n', '') + "|" + str(diffInMillSeconds))
           
        i = i + 1
        previous_date_time_str = date_time_str
        

    for row in printArray:            
        with open('timetaken.csv','a') as fd:            
            fd.write(instance + "|" + str(totalTimeTaken) + "|" + row + "\n")            

    totalTimeTaken=0
    i = 0
    printArray = []
