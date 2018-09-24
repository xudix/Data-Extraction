# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 02:31:29 2018

@author: Xudi

Data extraction and visulization tool
Based on the contribution of Miguel Petrarca

Class for tag picking dialog.
The dialog will be created when user push the "Choose Tags" button from main window
The button will invoke a static method getTags() in this class, which creates a diaglog
After picking tags in the window, the static method will return a string, 
which contains all tags separated by '/n'
"""

import tkinter as tk
import os.path
from tkinter.filedialog import askopenfilename


class PickTagWindow(tk.Frame):
    fontStr = "Helvetica 10"
    
    def __init__(self,master = None, mainWindowClass = None):
        # mainWindowClass is the main window, which contains information about the tag file path
        tk.Frame.__init__(self, master)
        # Make the window stretchable
        topLevelWindow = self.winfo_toplevel()                
        topLevelWindow.rowconfigure(0, weight = 1)            
        topLevelWindow.columnconfigure(0, weight = 1)
        topLevelWindow.title('Select Tags')
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)
        # Make it visible
        self.grid(sticky = tk.N+tk.S+tk.E+tk.W)
        # Method to create widgets
        self.createWidgets()
        # Register the behavior of some keys
        topLevelWindow.protocol("WM_DELETE_WINDOW", self.exitMethod)
        topLevelWindow.bind("<Return>", self.donePickTag)
        topLevelWindow.bind("<Escape>", self.exitMethod)
        # Prevent user from manipulating the main window
        topLevelWindow.grab_set()
        
        
        # Set the default file path
        if mainWindowClass:
            self.filePath = mainWindowClass.filePath
            self.tagFileName = mainWindowClass.tagFileName
        else:
            self.filePath = '/'
            self.tagFileName = 'TagList'
        # Call the loadTags function to load tags
        self.loadTagsFromFile()
        # Return the default file path
        if mainWindowClass:
            mainWindowClass.filePath = self.filePath
            mainWindowClass.tagFileName = self.tagFileName
        # Bring the window to front
        topLevelWindow.lift()
        
        
    def createWidgets(self):
        self.tagScrollY = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.tagListBox = tk.Listbox(self, width = 30, height = 15, font = self.fontStr, yscrollcommand = self.tagScrollY.set, 
                                     selectmode = tk.MULTIPLE)
        self.tagScrollY['command'] = self.tagListBox.yview
        self.doneButton = tk.Button(self, text = 'Done', font = self.fontStr, command = self.donePickTag)
        self.tagScrollY.grid(row = 0, column = 1, sticky = tk.N+tk.S+tk.W)
        self.tagListBox.grid(row = 0, column = 0, sticky = tk.N+tk.S+tk.W+tk.E)
        self.doneButton.grid(row = 1, column = 1, sticky = tk.E)
        self.doneButton.focus_set()
        
    def donePickTag(self, event = None): # Include event to allow binding to "Enter" key
        self.lineNumberSelected = self.tagListBox.curselection()
        self.itemsSelected = ''.join(str(self.tagList[j]) for j in self.lineNumberSelected)
        self.winfo_toplevel().destroy()
        
    def exitMethod(self, event = None):
        self.itemsSelected = ''
        self.winfo_toplevel().destroy()
        
    def loadTagsFromFile(self):
    # Prompt user to pick a file. If a file was previously picked, it will start at the same file
    # The Tag List file is a text file. All available tags will be listed. Each line will be one tag
        filePathName = askopenfilename(initialdir = self.filePath, initialfile = self.tagFileName, defaultextension = '.txt',
                                                           title = "Select Tag List File", filetypes = (("txt files","*.txt"), ("all files","*.*")))
        if filePathName:
            # Record the path and name of the picked file. Will start with the same file next time
            (self.filePath, self.tagFileName) = os.path.split(filePathName)
            with open(filePathName, 'r') as tagFile:
                # Take the tag file as a List object
                self.tagList = list(tagFile)
                for item in self.tagList:
                    self.tagListBox.insert(tk.END,str(item))
        
    @staticmethod
    def getTags(master = None):
        root = tk.Toplevel(master)
        pickTagDialog = PickTagWindow(root, master)
        pickTagDialog.wait_window()
        #if master:
        #    master.focus_set()
        return pickTagDialog.itemsSelected