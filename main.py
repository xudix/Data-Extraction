# -*- coding: utf-8 -*-
'''
Created on Sun Sep  2 03:31:20 2018

@author: Dikai Xu

Data extraction and visulization tool
Based on the contribution of Miguel Petrarca
'''
#import matplotlib
#matplotlib.use('TkAgg', warn=False, force=True)

import tkinter as tk
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showerror
import os.path
#import datetime

import callback_functions
import pick_tag
#import plotting


# class for Main window
class MainWindow(tk.Frame):
    fontStr  =  'Helvetica 10 bold'
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        # Make the window stretchable
        topLevelWindow = self.winfo_toplevel()                
        topLevelWindow.rowconfigure(0, weight = 1)            
        topLevelWindow.columnconfigure(0, weight = 1)
        topLevelWindow.title('Data Plotter: Data Extraction and Visulization')  
        self.rowconfigure(3, weight = 1)           
        self.columnconfigure(4, weight = 1) 
        # Make it visible
        self.grid(sticky = tk.N+tk.S+tk.E+tk.W)
        # Method to create widgets
        self.createWidgets()
        # Register the behavior of some keys
        topLevelWindow.protocol("WM_DELETE_WINDOW", self.exitMethod)
        topLevelWindow.bind("<Return>", self.plot)
        topLevelWindow.bind("<Escape>", self.exitMethod)
        # Set blank file paths for tags and data
        self.tagFileName = 'TagList'
        self.filePath = '/'
        # Lists to hold the handles to various plots
        self.plotWindows = []

        
        
    def createWidgets(self):
        # Create and show labels
        self.strDateLabel = tk.Label(self,text = 'Start Date',font = self.fontStr)
        self.strDateLabel.grid(row = 0, column = 0,sticky  =  tk.W)
        self.endDateLabel  =  tk.Label(self,text  =  'End Date',font  =  self.fontStr)
        self.endDateLabel.grid(row = 1, column = 0,sticky = tk.W)
        self.strTimeLabel = tk.Label(self,text = 'Start Time',font = self.fontStr)
        self.strTimeLabel.grid(row = 0, column = 3,sticky = tk.W)
        self.endTimeLabel = tk.Label(self,text = 'End Time',font = self.fontStr)
        self.endTimeLabel.grid(row = 1, column = 3,sticky = tk.W)
        self.tagLabel = tk.Label(self,text = 'Tags',font = self.fontStr)
        self.tagLabel.grid(row = 2, column = 0,sticky = tk.W)
        self.fileLabel = tk.Label(self,text = 'Data Files',font = self.fontStr)
        self.fileLabel.grid(row = 2, column = 3,sticky = tk.W)
        #Create input boxes
        self.strDateEntry = tk.Entry(self, width = 10, exportselection = 0)
        self.strTimeEntry = tk.Entry(self, width = 10, exportselection = 0)
        self.endDateEntry = tk.Entry(self, width = 10, exportselection = 0)
        self.endTimeEntry = tk.Entry(self, width = 10, exportselection = 0)
        self.strDateEntry.grid(row = 0, column = 1,sticky = tk.W)
        self.strTimeEntry.grid(row = 0, column = 4,sticky = tk.W)
        self.endDateEntry.grid(row = 1, column = 1,sticky = tk.W)
        self.endTimeEntry.grid(row = 1, column = 4,sticky = tk.W)
        #Create Buttons
        self.tagButton  =  tk.Button(self, text = 'Choose Tags', font = self.fontStr, command = self.pickTag)
        self.fileButton  =  tk.Button(self, text = 'Choose Data Files', font = self.fontStr, command = self.pickFiles)
        self.plotButton  =  tk.Button(self, text = 'Plot', font = self.fontStr, command = self.plot)
        self.tagButton.grid(row = 2, column = 1,sticky = tk.W)
        self.fileButton.grid(row = 2, column = 4,sticky = tk.W)
        self.plotButton.grid(row = 5, column = 4,sticky = tk.E)
        #Create Text widgets for inputing tags and files
        self.tagScrollY = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.fileScrollX = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.fileScrollY = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.tagEditBox = tk.Text(self, width = 30, height = 15, font = self.fontStr, 
                               undo = True, maxundo = 512, autoseparators=True, 
                               yscrollcommand = self.tagScrollY.set)
        self.fileEditBox = tk.Text(self, width = 80, height = 15, font = self.fontStr, 
                                undo = True, maxundo = 512, autoseparators=True, 
                                 xscrollcommand = self.fileScrollX.set, 
                                  yscrollcommand = self.fileScrollY.set, 
                                  wrap=tk.NONE)
        self.tagScrollY['command'] = self.tagEditBox.yview
        self.fileScrollX['command'] = self.fileEditBox.xview
        self.fileScrollY['command'] = self.fileEditBox.yview
        self.tagEditBox.grid(row = 3, column = 0, columnspan = 2,
                          sticky = tk.N+tk.S+tk.W+tk.E)
        self.fileEditBox.grid(row = 3, column = 3, columnspan = 2,
                           sticky = tk.N+tk.S+tk.W+tk.E)
        self.tagScrollY.grid(row = 3, column = 2, sticky = tk.N+tk.S+tk.W)
        self.fileScrollX.grid(row = 4, column = 3, columnspan = 2, sticky = tk.E+tk.N+tk.W)
        self.fileScrollY.grid(row = 3, column = 5, sticky = tk.N+tk.S+tk.W)
        
    def pickTag(self):
        # Prompt user to select tags from a list
        self.tagEditBox.insert(tk.END, pick_tag.PickTagWindow.getTags(self))
            
    def pickFiles(self):
        # Prompt user to select data files
        self.fileList = askopenfilenames(initialdir = self.filePath, defaultextension = '.csv', title = 'Select Data Files', 
                                         filetypes = (('CSV files','*.csv'), ('TXT files','*.txt'), ('All files','*.*')))
        # Normally, the files returned by askopenfilenames is a tuple. Each element will be a str
        # When no file is chosen, the return value is ''
        # if file is chosen, get the directory name. Will open from the same location next time
        if self.fileList:
            self.filePath = os.path.dirname(self.fileList[0])
            #print('filePath updated: '+self.filePath)
            for item in self.fileList:
                self.fileEditBox.insert(tk.END, item+'\n')
        
        
    def plot(self, event = None):
        # Take the inputs from user, and 
        try:
            callback_functions.parseInput(self)
        except Exception as err:
            showerror('Error Processing Input', str(err))
            return
        # PlotWindow class create a tkinter Toplevel widget and put the plot in it.
        # To put plot in tkinter GUI, need to use TkAgg backend and FigureCanvasTkAgg method to create the canvas widget from Figure
        # self.plotWindows.append(plotting.PlotWindow(self,self.startDateTime,self.endDateTime,self.tagList, self.fileList))
        
        # Alternative method, use the pyplot module
        self.plotWindows.append(callback_functions.plot2(self, self.startDateTime, self.endDateTime, self.tagList, self.fileList))

    def exitMethod(self, event = None):
        self.quit()
        self.winfo_toplevel().destroy()
        

app  =  MainWindow()
app.mainloop()