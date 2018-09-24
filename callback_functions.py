# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 06:58:25 2018

@author: Xudi
Data extraction and visulization tool
Based on the contribution of Miguel Petrarca

This file contains callback functions for widgets in the main GUI
"""

import tkinter as tk
import os.path
import re
import datetime
import time
import pandas as pd

import matplotlib.pyplot as plt

# Method to convert the user inputs in main window (strings) to instance attributes
def parseInput(self):
    # Check if the date and time provided by the user is valid, and parse input
    try:
        year, month, day = parseDate(self.strDateEntry.get())
        hour, minute, second = parseTime(self.strTimeEntry.get())
        self.startDateTime = datetime.datetime(year,month,day,hour,minute,second)
    except:
        raise ValueError('Invalid Start Date or Time')
        
    try:
        dateStr = self.endDateEntry.get()
        if dateStr != '': # If the end date is not given, use the same date as start
        # If the end date is given, parse it
            year, month, day = parseDate(dateStr)
        else:
            self.endDateEntry.insert(0,self.strDateEntry.get())
        hour, minute, second = parseTime(self.endTimeEntry.get())
        self.endDateTime = datetime.datetime(year,month,day,hour,minute,second)
    except:
        raise ValueError('Invalid End Date or Time')
    # If the end time is earlier than start time, swap them
    if self.startDateTime > self.endDateTime:
        temp = self.startDateTime
        self.startDateTime = self.endDateTime
        self.endDateTime = temp
    # Convert the string in tag edit box into tags separated by \n, then split it into a list
    # Tag input separated by any white space character or comma (,) is acceptable
    # Assume that the tag names do not contain any white spaces
    try:
        self.tagList = re.sub(r'[\s,]','\n',self.tagEditBox.get('1.0',tk.END)).split()
    # Remove the empty entries in the tag List
        i=0
        while i < len(self.tagList):
            if self.tagList[i] == '':
                self.tagList.pop(i)
            else:
                i=i+1
    except:
           raise ValueError('Invalid Tag List')
    # Convert the string in data file edit box into files separated by \n, then split it into a list
    # File input separated by line feed (\n) or character or comma (,) is acceptable
    try:
        fileStr = self.fileEditBox.get('1.0',tk.END).replace(',','\n')
        self.fileEditBox.delete('1.0',tk.END)
        self.fileEditBox.insert(tk.END,fileStr.strip())
        self.fileList = fileStr.split('\n')
        # Remove the empty entries in the file List
        # Also record the start time and file types for all data files
        i=0
        while i < len(self.fileList):
            if self.fileList[i] == '': # Empty entry. Will be removed
                self.fileList.pop(i)
            else:
                # A file. Will record the start time of the files, and the file types
                # Assume the data files have names in format: {Date}-{Time}.{extension}
                # Normally the files are YYYYMMDD-HHmmSS.csv
                m = re.search('([0-9]{8})[\W_]*([0-9]{6})\.(\w+)$', self.fileList[i])
                if m:
                    year, month, day = parseDate(m[1])
                    hour, minute, second = parseTime(m[2])
                else: # no match. Other allowered file name format requires separation between date and time
                    raise ValueError('Invalid Data File Name: '+os.path.basename(self.fileList[i]))
                # The fileList will become a list of tuples. [(filePathName, startDateTime, extension)]
                self.fileList[i] = (self.fileList[i], datetime.datetime(year,month,day,hour,minute,second), m[3])
#                self.fileStartTimeList.insert(i,datetime.datetime(year,month,day,hour,minute,second))
#                self.fileExtensionList.insert(i,m[3])
                # Go to the next item in the list
                i += 1
        # Sort the fileList in chronological order
        # The lambda expression represents a function that takes the second member of the tuple, which is the start datetime
        self.fileList.sort(key=lambda fileRecord: fileRecord[1])
        # Determine which data files are needed
        
        if self.endDateTime < self.fileList[0][1]:
            raise ValueError('Requested Date and Time Not Available in Selected Data Files')
        else:
            # when there's more than one file, check their start time
            # only files needed will be left in the filelist
            if len(self.fileList) > 1:
                i = 0
                while i < len(self.fileList)-1:
                    if self.fileList[i+1][1] <= self.startDateTime: # Next file start before startDateTime. This file is not needed
                        self.fileList.pop(i)
                    else: # Next file start after startDateTime. This file is needed
                        if self.fileList[i+1][1] > self.endDateTime: # Next file start after endDateTime. Later files will not be needed
                            del self.fileList[i+1:]
                            break
                        i += 1
    except Exception as err:
        raise ValueError('Invalid Data File List\n'+str(err))
 
    
def parseDate(dateStr): # return (int year,int month,int day)
    # try to parse the data string into year, month, and day.
    # If the format cannot be sucessfully converted to a date, ValueError is raised
    
    # If the input contains things like 1st, 2nd, 3rd, 4th, remove the st/nd/rd/th and replace by space
    dateStr = re.sub(r'(\d+)(st|nd|rd|th)',r'\1 ',dateStr, 0,re.I)
    # If the input contains any letters, assume they are literal months. Add space before and after
    dateStr = re.sub(r'([a-zA-Z]+)',r' \1 ',dateStr, 0,re.I)
    # Split the dateStr if it contains seperators: ,./\|-_ and other blank space
    #dateList = re.split(r'[\\.,:;\'\"=+<>~`/\-_\s]+',dateStr) # re.split() returns a List object
    dateList = re.split(r'[\W_]+',dateStr) # re.split() returns a List object
    # remove all empty string in the date List
    i = 0
    while i < len(dateList):
        if dateList[i] == '':
            dateList.pop(i)
        else:
            i=i+1
    if len(dateList) == 1 and dateList[0].isdigit(): 
        
        strLength = len(dateList[0])
        dateInt = int(dateList[0])
    # Regular expression not matching. The date format is pure number
        if strLength == 4 or strLength == 3: # This is the MMDD format. Will use current year
            year = int(time.strftime('%Y'))
            month = dateInt//100
            day = dateInt%100
        elif strLength == 2: # Only two digits. Treat it as MD
            year = int(time.strftime('%Y'))
            month = dateInt//10
            day = dateInt%10
        elif  strLength == 6: # This is the YYMMDD or MMDDYY format.
            # default is YYMMDD, unless last two digits are greater than 31 or middle two freater than 12
            year = dateInt//10000+2000
            month = (dateInt//100)%100
            day = dateInt%100
            if month >12 or day>31 or day == 0: #MMDDYY format
                year = dateInt%100+2000
                month = dateInt//10000
                day = (dateInt//100)%100
                if month >12 or day>31: #DDMMYY format
                    month = (dateInt//100)%100
                    day = dateInt//10000
        elif strLength == 5: # MDDYY format
            year = dateInt%100+2000
            month = dateInt//10000
            day = (dateInt//100)%100
        elif strLength == 8: # YYYYMMDD or MMDDYYYY format
            # default is YYYYMMDD format
            year = dateInt//10000
            month = (dateInt//100)%100
            day = dateInt%100
            if month >12 or day>31 or day == 0: #MMDDYYYY format
                year = dateInt%10000
                month = dateInt//1000000
                day = (dateInt//10000)%100
                if month >12 or day>31: #DDMMYYYY format
                    month = (dateInt//10000)%100
                    day = dateInt//1000000
#            if int(dateStr[4:6])<13: # YYYYMMDD format
#                year = int(dateStr[0:4])
#                month = int(dateStr[4:6])
#                day = int(dateStr[6:8])
#            else: #MMDDYYYY format
#                year = int(dateStr[4:8])
#                month = int(dateStr[0:2])
#                day = int(dateStr[2:4])
        elif strLength == 7: # MDDYYYY or DMMYYYY format
            year = dateInt%10000
            month = dateInt//1000000
            day = (dateInt//10000)%100
            if month >12 or day>31: #DDMMYYYY format
                month = (dateInt//10000)%100
                day = dateInt//1000000
        else: # Any other cases should generate an exception
            raise ValueError('Invalid Date')    
        
    elif len(dateList) >= 3: #Regular expression found separators. Year, Month and Day are all given
        if dateList[0].isalpha(): # It's MMDDYYYY format, month is written in text
            # Dictionary to convert literal month to number
            monthDict = dict(JAN=1, JANUARY=1, FEB=2, FEBRUARY=2, MAR=3, MARCH=3, APR=4, APRIL=4,
                             MAY=5, JUN=6, JUNE=6, JUL=7, JULY=7, AUG=8, AUGUST=8, SEP=9, SEPT=9, 
                             SEPTEMBER=9, OCT=10, OCTOBER=10, NOV=11, NOVEMBER=11, DEC=12, DECEMBER=12)
            try:
                month = monthDict[dateList[0].upper()]
                year = int(dateList[2])
                if year<100: # MMDDYY format
                    year += 2000
                day = int(dateList[1])
            except:
                raise ValueError('Invalid Date') 
        elif dateList[1].isalpha(): # YYYYMMDD or DDMMYYYY format, month is written in text 
            # Dictionary to convert literal month to number
            monthDict = dict(JAN=1, JANUARY=1, FEB=2, FEBRUARY=2, MAR=3, MARCH=3, APR=4, APRIL=4,
                             MAY=5, JUN=6, JUNE=6, JUL=7, JULY=7, AUG=8, AUGUST=8, SEP=9, SEPT=9, 
                             SEPTEMBER=9, OCT=10, OCTOBER=10, NOV=11, NOVEMBER=11, DEC=12, DECEMBER=12)
            try:
                month = monthDict[dateList[1].upper()]
                # default if YYYYMMDD format, unless the last part of dateList is greater than 31
                if len(dateList[0]) >= 2 and int(dateList[2])<=31:
                    year = int(dateList[0])
                    day = int(dateList[2])
                else: # DDMMYYYY
                    year = int(dateList[2])
                    day = int(dateList[0])
                if year<100: # MMDDYY format
                    year += 2000
            except:
                raise ValueError('Invalid Date') 
        elif dateList[0].isdigit() and dateList[1].isdigit() and dateList[2].isdigit():
            # Inputs are all digits. 
            if len(dateList[2])==4: # MMDDYYYY (default) or DDMMYYYY format
                year = int(dateList[2])
                if int(dateList[0])<=12: # MMDDYYYY
                    month = int(dateList[0])
                    day = int(dateList[1])
                else: # DDMMYYYY
                    month = int(dateList[1])
                    day = int(dateList[0])
            elif len(dateList[0])==4: # YYYYMMDD format
                year = int(dateList[0])
                month = int(dateList[1])
                day = int(dateList[2])
            # YYMMDD or MMDDYY or DDMMYY format
            elif len(dateList[0]) >= 2 and int(dateList[1])<=12 and int(dateList[2])<=31:
                year = int(dateList[0])+2000
                month = int(dateList[1])
                day = int(dateList[2])
            elif int(dateList[0]) <12 and int(dateList[1])<31: # MMDDYY format
                year = int(dateList[2])+2000
                month = int(dateList[0])
                day = int(dateList[1])
            else: # DDMMYY format
                year = int(dateList[2])+2000
                month = int(dateList[1])
                day = int(dateList[0])
        else:
            raise ValueError('Invalid Date')  
    elif len(dateList) == 2: # Only month and day is given. Assume current year
        year = int(time.strftime('%Y'))
        if dateList[0].isalpha(): # It's MMDDYYYY format, month is written in text
            # Dictionary to convert literal month to number
            monthDict = dict(JAN=1, JANUARY=1, FEB=2, FEBRUARY=2, MAR=3, MARCH=3, APR=4, APRIL=4,
                             MAY=5, JUN=6, JUNE=6, JUL=7, JULY=7, AUG=8, AUGUST=8, SEP=9, SEPT=9, 
                             SEPTEMBER=9, OCT=10, OCTOBER=10, NOV=11, NOVEMBER=11, DEC=12, DECEMBER=12)
            try:
                month = monthDict[dateList[0].upper()]
                day = int(dateList[1])
            except:
                raise ValueError('Invalid Date') 
        elif dateList[1].isalpha(): # DDMM format, month is written in text 
            # Dictionary to convert literal month to number
            monthDict = dict(JAN=1, JANUARY=1, FEB=2, FEBRUARY=2, MAR=3, MARCH=3, APR=4, APRIL=4,
                             MAY=5, JUN=6, JUNE=6, JUL=7, JULY=7, AUG=8, AUGUST=8, SEP=9, SEPT=9, 
                             SEPTEMBER=9, OCT=10, OCTOBER=10, NOV=11, NOVEMBER=11, DEC=12, DECEMBER=12)
            try:
                month = monthDict[dateList[1].upper()]
                day = int(dateList[0])
            except:
                raise ValueError('Invalid Date') 
        elif dateList[0].isdigit() and dateList[1].isdigit():
            if int(dateList[0])>12: # DDMM format
                month = int(dateList[1])
                day = int(dateList[0])
            else: #MMDD format
                month = int(dateList[0])
                day = int(dateList[1])
        else:
            raise ValueError('Invalid Date') 
    else:
        raise ValueError('Invalid Date')
    if day < 1 or day>31 or month < 1 or month > 12:
        raise ValueError('Invalid Date')
    elif month in (4,6,9,11) and day > 30:
        raise ValueError('Invalid Date')
    elif month == 2 and day>29:
        raise ValueError('Invalid Date')
        
    return (year, month, day)
        
def parseTime(timeStr):
    # parse a string to time
    # timeStr = timeStr.lower()
    
    # if there is 'p' or 'pm' in the timeStr, we may need to add 12 to Hour
    if re.search(r'p|pm', timeStr, re.I):
        timeStr = re.sub(r'pm*','', timeStr, re.I)
        isPM = True
    else:
        isPM = False
    # if there is 'a' or 'am' in the timeStr, set a flag to deal with 12am
    if re.search(r'a|am', timeStr, re.I):
        timeStr = re.sub(r'am*','', timeStr, re.I)
        isAM = True
    else:
        isAM = False
    # remove all letters
    timeStr = re.sub(r'[a-zA-Z]+', '', timeStr, re.I)
    # split the str by symbols
    timeList = re.split(r'[\W_]+',timeStr)
    # remove all empty string in the time List
    i = 0
    while i < len(timeList):
        if timeList[i] == '':
            timeList.pop(i)
        else:
            i=i+1
    # No separator, all digits
    if len(timeList) == 1 and timeList[0].isdigit():
        strLength = len(timeList[0])
        timeInt = int(timeList[0])
        if strLength >= 5: #5 or 6 digits. Contains second
            second = timeInt%100
            minute = (timeInt//100)%100 # the // operator will make sure the result is int
            hour = timeInt//10000
        elif strLength >= 3: # 3 or 4 digits, only hour and minute
            second = 0
            minute = timeInt%100
            hour = timeInt//100
        elif timeInt >=1 and timeInt <=24: # 1 or 2 digits, only hour given
            second = 0
            minute = 0
            hour = timeInt
        else:
            raise ValueError('Invalid Time')
    elif len(timeList) == 2 and timeList[0].isdigit() and timeList[1].isdigit(): 
        # Hour and minute given
        hour = int(timeList[0])
        minute = int(timeList[1])
        second = 0
    elif len(timeList) >= 3 and timeList[0].isdigit() and timeList[1].isdigit() and timeList[2].isdigit():
        # Hour, minute, and second given
        hour = int(timeList[0])
        minute = int(timeList[1])
        second = int(timeList[2])
    else:
        raise ValueError('Invalid Time')
        
    #Check if the time is valid
    if hour > 25 or minute >59 or second>59 or hour < 0 or minute < 0 or second < 0:
        raise ValueError('Invalid Time')
    
    # if it's 0pm, 1pm, ... 11pm, add 12 to the hour number
    if isPM and hour >= 0 and hour < 12:
        hour += 12
    elif isAM and hour == 12: # if it's 12am, set hour to 0
        hour = 0
    # if hour is 24, set the time to last second of the day 23:59:59
    if hour == 24:
        hour = 23
        minute = 59
        second = 59
            
    return (hour, minute, second)

def getData(startDateTime, endDateTime, tagList, fileList, interval=1): 
    # Retrive data from data file
    # Return a Pandas DataFrame object with the requested time as the Index and tags as columns.
    # Go through the file list and open the files one by one
    dfToPlot = None
    for record in fileList: # A record is (file, startdatetime, extension)
        if record[2].lower() == 'csv': # csv file
        # Loading csv file with data into DataFrame object
            datadf = pd.read_csv(record[0])
        elif record[2].lower() == 'txt':
            datadf = pd.read_table(record[0])
        elif record[2].lower() == 'xls':
            break
        elif record[2].lower() == 'xlsx':
            break
        else:
            break
        
        #Replacing time column with the date time object version of the corresponding strings (actually the function changes strings to Timestamp objects)
        #this is done in order to be able to use logical operators and 
        if 'Date' in datadf: # if the csv file contains column 'Date', then 'Date' and 'Time' need to be merged
            # Concatenate date and time columns, both of type str, into a single string. Space in between the two is added for formatting
            datadf['Time'] = pd.to_datetime(datadf['Date'] + ' ' + datadf['Time'], format = '%m/%d/%Y %H:%M:%S')
        elif ';Date' in datadf:
            datadf['Time'] = pd.to_datetime(datadf[';Date'] + ' ' + datadf['Time'], format = '%m/%d/%Y %H:%M:%S')
        
        # In some cases, the first two rows of the csv is at the same time. Remove the 1st row if that's the case
        if datadf.at[0, 'Time'] == datadf.at[1, 'Time']:
            datadf = datadf[1:]
        # Check if all tags are in the csv file. If not, remove it.
        
        validTagList = tagList[:]
        i = 0
        while i < len(validTagList):
            if validTagList[i] in datadf:
                i += 1
            else:
                validTagList.pop(i)
        #We extract only the relevant time interval and store it in another DataFrame. Subset of datadf DataFrame
        #True for rows we want to extract False for rows outside specifed time range
        timeIntervalSeries = ((datadf['Time']<=endDateTime) & (datadf['Time']>=startDateTime)).values
        # Take the required data
        datadf.set_index('Time', inplace = True)
        datadf = datadf.loc[timeIntervalSeries,validTagList]
        
        # Remove time slices that are not needed
        if interval != 1:
        # If interval is given, take data every "interval" points
            datadf = datadf[::interval]
        
        if dfToPlot is None: # This is the first file. 
            dfToPlot = datadf.copy()
        else:  # not the first file. Append the things to the existing dfToPlot
            dfToPlot = dfToPlot.append(datadf)
    
    return dfToPlot


def plot2(self, startDateTime, endDateTime, tagList, fileList, interval=1):
    # Alternative method to make plot. Use the pyplot module of MatPlotLib. 
    # start datetime, end datetime, taglist, file list, and interval are given separately, so that the change in MainWindow does not affect the plots generated previously
    
    # Get data from the files
    dfToPlot = getData(startDateTime, endDateTime, tagList, fileList, interval)
    
    # Generate a figure and put it in the plotWindow list of the mainwindow
    fig = plt.figure(figsize=(3, 2), dpi=300)    
    
    for tag in dfToPlot.columns:
        if tag in dfToPlot:
            plt.plot(dfToPlot.index, dfToPlot[tag], label = tag, linewidth = 1)
            
    plt.legend(bbox_to_anchor=(1.04,1), loc="upper left", fontsize = 3)
    plt.xlabel('Time', fontsize = 5)
    plt.xticks(fontsize = 3)
    plt.yticks(fontsize = 3)
    plt.grid(True)
    plt.tight_layout()
    
    return fig