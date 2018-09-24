# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 02:31:29 2018

@author: Xudi

Data extraction and visulization tool
Based on the contribution of Miguel Petrarca

Class for plotting window

"""

import tkinter as tk
import os.path
from tkinter.filedialog import askopenfilename

import pandas as pd

import matplotlib
matplotlib.use('TkAgg', warn=False, force=True)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import matplotlib.style as mplstyle
mplstyle.use('fast')
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import callback_functions


class PlotWindow(tk.Toplevel):
    fontStr = "Helvetica 10"
    
    def __init__(self, master, startDateTime, endDateTime, tagList, fileList, interval=1):
        # start datetime, end datetime, taglist, file list, and interval are given separately, so that the change in MainWindow does not affect the plots generated previously
        # Master is the main window
        tk.Toplevel.__init__(self, master)
        self.title('Plot')
        # Make the window stretchable
        #self.rowconfigure(0, weight = 1)            
        #self.columnconfigure(0, weight = 1)
        
        # Method to create widgets
        self.createWidgets(master, startDateTime, endDateTime, tagList, fileList, interval)
        # Register the behavior of some keys
#        self.protocol("WM_DELETE_WINDOW", self.exitMethod)
#        self.bind("<Return>", self.donePickTag)
#        self.bind("<Escape>", self.exitMethod)
        
        
    def createWidgets(self, master, startDateTime, endDateTime, tagList, fileList, interval=1):
        # Create a Frame in the Toplevel to host the things
        self.frame = tk.Frame(self)
        #self.frame.grid(sticky = tk.N+tk.S+tk.E+tk.W)
        self.frame.pack(fill = tk.BOTH, expand = True, side = tk.BOTTOM)
        # Create plot
        self.fig = Figure(figsize=(3, 2), dpi=300)
        #self.axes = self.fig.add_axes([0, 0, 1, 1])
        self.axes = self.fig.add_subplot(111)
        # Plot the data in the figure
        self.plot(callback_functions.getData(startDateTime, endDateTime, tagList, fileList, interval))
        
        # Canvas created from matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        # Make the canvas resizable
        self.canvas.get_tk_widget().grid(row = 1, column = 1, sticky = tk.N+tk.S+tk.E+tk.W)
        self.frame.rowconfigure(1, weight = 1)            
        self.frame.columnconfigure(1, weight = 1)
        #self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # Create navigation toolbar. 
        # !! This is not compatible with grid() since the NavigationToolBar2TkAgg used pack()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self) # or (self.canvas, self) ??
        
        
    def plot(self, dfToPlot):
        # Plot data in the figure self.fig
        # This method will only deal with the things within the Figure
        # Data extraction complete
        # Start to plot
        for tag in dfToPlot.columns:
            if tag in dfToPlot:
                self.axes.plot(dfToPlot.index, dfToPlot[tag], label = tag, linewidth = 1)
        
        # Change font size of tick labels
        self.axes.tick_params(axis = 'both', labelsize = 3)
        # Draw legend
        # See https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot/43439132#43439132 for discussion
        self.axes.legend(loc=(1.04,0), fontsize = 3)
        # x-axis is titled 'Time'
        self.axes.set_xlabel('Time', fontsize = 5)
        
        self.axes.grid()
        # Make the Figure to adjust for all elements using tight_layout()
        self.fig.tight_layout()
        # Fonts
        
        
    def exitMethod(self, event = None):
        self.destroy()
        
