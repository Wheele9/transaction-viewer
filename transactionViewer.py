# coding: utf-8


import os
import inspect
import datetime
from datetime import date, timedelta
import copy
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.widgets import Button, SpanSelector, RadioButtons
from matplotlib.dates import num2date, DayLocator


class Presenter():
    
    def __init__(self, model, view, files):
        self.model = model
        self.view = view
        self.files = files
        
    def showPlots(self):
        self.cleanedDf, self.wholeDf = self.model.parseFiles(self.files)
        self.view.showPlots(self.cleanedDf)
    
    def showDataframe(self):
        return self.wholeDf


class otpParser():
    
    def __init__(self):
        self.headers = ['accountNr', 'T/J', 'sum', 'currency', 'date', 'date2', 'balance', 'noIdea',
                   'noIdea2', 'comment', 'noIdea3', 'noIdea4', 'comment2']
        
    def parseFiles(self, files):
        try:
            dataFrames = [pd.read_csv(file,  header=None) for file in files]
        except :
            dataFrames = [pd.read_csv(file, sep=';', header=None) for file in files]
            
        for df in dataFrames:
            try:
                df.drop(df.columns[[13, 14]], axis=1, inplace=True)
            except:
                pass
        
        mergedFrame = pd.concat(dataFrames)
        mergedFrame.columns = self.headers                                        
        mergedFrame = mergedFrame.reset_index(drop=True)
        mergedFrame = mergedFrame.sort_values(by='date')
        mergedFrame['comment'] = mergedFrame['comment'].replace(np.nan, '', regex=True)
        mergedFrame['comment'] = mergedFrame['comment'].apply((lambda x: ' '.join(x.split())))
        mergedFrame.loc[mergedFrame['comment']=='','comment'] = mergedFrame.loc[(mergedFrame["comment"] == '') , "comment2"]
        cleanDf = mergedFrame.loc[:,['sum', 'date', 'comment','balance']]
        return cleanDf, mergedFrame

    def printDf(self):
        return (self.mergedFrame.head())


RED = (0.83921568627450982, 0.15294117647058825, 0.15686274509803921, 1.0)
DARK_RED = (0.49803921568627452, 0.12156862745098039, 0.12156862745098039, 1.0)
GREY = (0.5019607843137255, 0.5450980392156862, 0.5882352941176471, 1)
GREEN = (0.098039215686274508, 0.43529411764705883, 0.23921568627450981, 1.0)
DARK_GREEN = (0.0078431372549019607, 0.25490196078431371, 0.0078431372549019607, 1.0)
PURPLE = (0.6666666666666666, 0.6745098039215687 ,0.8862745098039215,1.0)
LIGHT_GREEN =  (0.1568627450980392, 0.7058823529411765, 0.38823529411764707, 1.0)
LIGHT_RED = (1.0, 0.2784313725490196, 0.2784313725490196, 1.0)
LIGHT_GREY = (0.8352941176470589, 0.8470588235294118, 0.8627450980392157,1.0)

WIDTH = 12
G_RAT = (1 + 5 ** 0.5) / 2 # golden ratio
LABEL_ROTATION = 15 # DEGREES
DATEFORMATSTRING = '%Y-%m-%d'
DATEFROMAT = mdates.DateFormatter(DATEFORMATSTRING)
# to highlight recatangles
dark2light={DARK_RED:LIGHT_RED, DARK_GREEN:LIGHT_GREEN}
# to unhighlight recatangles
dark2normal={DARK_RED:RED, DARK_GREEN:GREEN}
light2normal={LIGHT_RED:RED, LIGHT_GREEN:GREEN}
    
class financeViewer():
    
    def __init__(self):

        self.box = dict(facecolor='blue', pad=3, alpha=0.2, boxstyle="Round4,pad=0.3")
        self.testString ="""Date: {}
                            Sum: {} HUF
                            Comment: {}"""
        self.scale1='log'
        self.scale2='log'
        self.mode = 'transaction' # the other mode is balance mode, modifies the top plot
        
        self.start, self.end = None, None
    
    def createFigure(self):
        # disable toolbar
        matplotlib.rcParams['toolbar'] = 'None'
        self.fig = plt.figure(figsize=(WIDTH, WIDTH/G_RAT),facecolor = LIGHT_GREY)

        self.gsp = gridspec.GridSpec(
                nrows = 3, ncols = 2, wspace = 0.05, hspace = 0.45,
                width_ratios = [G_RAT, 1], height_ratios = [(1+G_RAT)/G_RAT, G_RAT, 1])

        self.ax1 = plt.subplot(self.gsp[0,:])
        self.ax2 = plt.subplot(self.gsp[1:,0])
        self.ax3 = plt.subplot(self.gsp[2,1])
        self.ax4 = plt.subplot(self.gsp[1,1])

    def drawAxes(self):

        for ax in [self.ax1,self.ax2,self.ax3, self.ax4]: 
            ax.set_facecolor(GREY)
            
        #####BIG PLOT##       
        self.plotAx1()
        
        ####ZOOM PLOT##
        self.plotAx2()
        
        ##info plot##
        self.txt = self.ax3.text(0.1,0.5,self.testString.format('','',''),
        horizontalalignment='left',
        verticalalignment='center',
        fontsize=13, color='black',
        wrap = True)
        self.ax3.set_xticks([]) 
        self.ax3.set_yticks([]) 
        self.ax3.set_title('info about the transactions', bbox=self.box)

        ### place of buttons##
        self.ax4.set_xticks([]) 
        self.ax4.set_yticks([]) 

    def on_plot_hover(self, event):

        if not event.inaxes: return
        if event.inaxes!= self.ax2: return

        for idx,bar in enumerate(self.ax2.patches):
            if bar.get_x() < event.xdata < bar.get_x() + bar.get_width():
                if bar.get_y() < event.ydata < bar.get_y() + bar.get_height(): 

                    self.ax2.patches[idx].set_facecolor(dark2light[bar.get_edgecolor()])
                    date_ordinal, y = self.ax2.transData.inverted().transform([event.x, event.y])+0.5
                    
                    # convert the numeric date into a datetime
                    transDate = num2date(date_ordinal).strftime(DATEFORMATSTRING)
                    pdDate = num2date(date_ordinal).strftime('%Y%m%d')
                    try:
                        comment = self.cleanDf.loc[(self.cleanDf['date'] == int(pdDate)) & (abs(self.cleanDf['sum'],)==bar.get_height()),'comment'].iloc[0]
                    except:
                        comment='Record not found'

                    newStr = self.testString.format(transDate,bar.get_height(), comment)
                    self.txt.set_text(newStr)
            else:
                self.ax2.patches[idx].set_facecolor(dark2normal[bar.get_edgecolor()])
        self.fig.canvas.draw()

    def reset_button_on_clicked(self, mouse_event):        
        self.plotAx2()

    def balanceView_button_on_clicked(self, mouse_event):
        self.txt.set_text('Not implemented yet')

    def transView_button_on_clicked(self, mouse_event):
        self.txt.set_text('Not implemented yet')

    def plotAx2(self,):  
        self.ax2.cla()
        self.ax2.set_title('Selected duration', bbox=self.box)
        if self.start != None:
            startDate = self.pdRange[self.start]
            endDate = self.pdRange[self.end]
            currentRange = pd.date_range(start=startDate, end=endDate, periods=None, freq='D', )
            indexes = []
               
            for idx, day in enumerate(self.incomeX):
                if (len(np.where(currentRange==day)[0])):
                    indexes.append(idx)
            currIncomeX = np.array(self.incomeX)[indexes]
            currIncomeY = np.array(self.incomeY)[indexes]

        else:
            currentRange = self.pdRange
            currIncomeX = self.incomeX
            currIncomeY = self.incomeY
            
        baseArray = np.zeros(len(currentRange),dtype=np.float)
        
        self.ax2.bar(currIncomeX, currIncomeY, color=GREEN, edgecolor=DARK_GREEN)
        
        for expenseX, expenseY in zip(self.expenseXs, self.expenseYs):
            ## calculate bottom for this iteration
            currBottomIdxs =[]
            indexes = []

            for idx, day in enumerate(expenseX):
                if len(np.where(currentRange==day)[0]):
                    currBottomIdxs.append(np.where(currentRange==day)[0][0])
                    indexes.append(idx)

            expenseX = np.array(expenseX)[indexes]
            expenseY = np.array(expenseY)[indexes]
            bottom = baseArray[currBottomIdxs]
            self.ax2.bar(expenseX,expenseY,bottom=bottom, color=RED, edgecolor=DARK_RED)
            ### calculate baseArray for the next iteration

            baseArray[currBottomIdxs] += expenseY
            
        if self.start and self.end-self.start <= 4:
            self.ax2.xaxis.set_major_locator(DayLocator())
        
        self.ax2.xaxis.set_major_formatter(DATEFROMAT)
        self.ax2.set_yscale(self.scale2, nonposy='clip')
        self.ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        plt.setp( self.ax2.xaxis.get_majorticklabels(), rotation=LABEL_ROTATION )
        
    def plotAx1(self):
        
        self.ax1.cla()
        self.ax1.set_title('Whole duration',bbox=self.box)
        
        if self.mode == 'transaction':
            self.plotAx1_transaction()
        elif self.mode == 'balance':
            self.plotAx1_balance()
        else :
            raise ValueError('selected mode not supported:  %s' % self.mode)
            
                    
        self.span = SpanSelector(self.ax1, self.onselect, 'horizontal', 
                       rectprops=dict(alpha=0.3, facecolor=RED))
            
        self.ax1.xaxis.set_major_formatter(DATEFROMAT)
        self.ax1.set_yscale(self.scale1, nonposy='clip')
        self.ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        plt.setp( self.ax1.xaxis.get_majorticklabels(), rotation=LABEL_ROTATION )
      
    def plotAx1_balance(self):

        self.ax1.step(self.pdDates, self.balance, marker="d", color = DARK_RED) 
    
    def plotAx1_transaction(self):
        self.ax1.bar(self.incomeX, self.incomeY, color=GREEN,edgecolor=DARK_GREEN)
            
        baseArray = np.zeros(len(self.pdRange),dtype=np.float)
        for expenseX, expenseY in zip(self.expenseXs, self.expenseYs):
            ## calculate bottom for this iteration
            currBottomIdxs = [np.where(self.pdRange==day)[0][0] for day in expenseX]
            bottom = baseArray[currBottomIdxs]
            self.ax1.bar(expenseX,expenseY,bottom=bottom, color=RED, edgecolor=DARK_RED)
            ### calculate baseArray for the next iteration

            baseArray[currBottomIdxs] += expenseY            
        
    def onselect(self, xmin, xmax):

        dayMin, dayMax = sorted((int(xmin-0.5), int(xmax+0.5)))
        ##xmin, xmax is days from zero, if Xaxis is pandas daterange
        yearZero = datetime.datetime.strptime('0001/01/01', "%Y/%m/%d")
        startDate = yearZero + timedelta(days=dayMin)
        endDate = yearZero + timedelta(days=dayMax)
        st=str(startDate)[:10]
        nd=str(endDate)[:10]
        stIdx, = np.where( self.pdRange.values==np.datetime64(st) )
        endIdx, = np.where( self.pdRange.values==np.datetime64(nd) )

        try:
            stIdx , endIdx = stIdx[0], endIdx[0]
        except:
            try:
                stIdx , endIdx = 0, endIdx[0]

            except:
                stIdx , endIdx = stIdx[0], len(self.pdRange)-1

        self.start, self.end = stIdx, endIdx
        self.plotAx2()
        self.fig.canvas.draw()
        
    def makeButtons(self):

        pos = self.ax4.get_position() # get the  position of axis ,which contains the buttons 
        self.ax4.set_title('plot properties',bbox=self.box)
        rowNr, colNr = 2,2
        buttonwidth = 0.13
        buttonheight = 0.07
        Vspace = (pos.width - colNr*buttonwidth)/(colNr+1)
        Hspace = (pos.height - rowNr*buttonheight)/(rowNr+1)
        ## radio buttons
        scaleSelectorAx1 = self.fig.add_axes([pos.x0+Vspace, pos.y0+2*Hspace+buttonheight, buttonwidth, buttonheight],facecolor=PURPLE)
        scaleSelectorAx2 = self.fig.add_axes([pos.x0+Vspace, pos.y0+Hspace, buttonwidth, buttonheight],facecolor=PURPLE)
        modeSelectorAx1 = self.fig.add_axes([pos.x0+2*Vspace+buttonwidth, pos.y0+2*Hspace+buttonheight, buttonwidth, buttonheight],facecolor=PURPLE)
        
        scaleSelectorAx1.set_title('top plot scale',fontsize=12)
        scaleSelectorAx2.set_title('bottom plot scale',fontsize=12)
        modeSelectorAx1.set_title('top plot mode',fontsize=12)
        
        axcolor = PURPLE
        self.scaleSelector1 = RadioButtons(scaleSelectorAx1, ('logaritmic','linear'))
        self.scaleSelector2 = RadioButtons(scaleSelectorAx2, ('logaritmic','linear'))
        self.modeSelector = RadioButtons(modeSelectorAx1, ('transaction view', 'balance view'))
        
        for button in [self.scaleSelector1, self.scaleSelector2, self.modeSelector]:
            for circle in button.circles: # adjust radius here. The default is 0.05
                circle.set_radius(0.09)
                circle.set_edgecolor('black')
                
        ## small buttons
        resetAx = self.fig.add_axes([pos.x0+2*Vspace+buttonwidth, pos.y0+Hspace, buttonwidth/2, buttonheight])
        helpAx = self.fig.add_axes([pos.x0+2*Vspace+1.5*buttonwidth, pos.y0+Hspace, buttonwidth/2, buttonheight])
        self.resetBtn = Button(resetAx, 'Reset', color = PURPLE, hovercolor = DARK_RED)
        self.helpBtn = Button(helpAx, 'About', color = PURPLE, hovercolor = DARK_RED)

    def resetClicked(self,event):

        self.scale1='log'
        self.scale2='log'
        self.mode = 'transaction'
        self.start=None
        self.end = None
        self.plotAx1()
        self.plotAx2()
        self.scaleSelector1.set_active(0)
        self.scaleSelector2.set_active(0)
        self.modeSelector.set_active(0)
        self.fig.canvas.draw()

    def helpClicked(self,event):
        pass
        print ('help')
        helpText = """Go to
        github.com/Wheele9/transaction-viewer
        to get the latest version, 
        to create an issue or pull request.
        Feel free to contact me."""
        self.txt.set_text(helpText)
    
    def modeButtonClicked(self, label):
        print (label)
        if label == 'balance view':
            if self.mode == 'balance': return
            self.mode = 'balance'
            self.scale1 = 'linear'
            self.plotAx1()
        elif label == 'transaction view':
            if self.mode == 'transaction': return
            self.mode = 'transaction'
            self.plotAx1()
        else: 
            raise ValueError('could not find %s' % label)
        print ('clicked,', self.mode)
        self.fig.canvas.draw()
            
    def scaleButton1Clicked(self, label):

        if label == 'linear':
            if self.scale1 == 'linear': return
            self.scale1='linear'
            self.plotAx1()
        elif label == 'logaritmic':
            if self.scale1 == 'logaritmic': return
            self.scale1='log'
            self.plotAx1()
        else: raise ValueError('could not find %s' % label)
        self.fig.canvas.draw()
        
    def scaleButton2Clicked(self, label):

        if label == 'linear':
            if self.scale2 == 'linear': return
            self.scale2='linear'
            self.plotAx2()
        elif label == 'logaritmic':
            if self.scale2 == 'logaritmic': return
            self.scale2='log'
            self.plotAx2()
        else: raise ValueError('could not find %s' % label)
        self.fig.canvas.draw()
        
    def connectButtons(self):

        self.scaleSelector1.on_clicked(self.scaleButton1Clicked)
        self.scaleSelector2.on_clicked(self.scaleButton2Clicked)
        self.modeSelector.on_clicked(self.modeButtonClicked)
        
        self.resetBtn.on_clicked(self.resetClicked)
        self.helpBtn.on_clicked(self.helpClicked)
      
    def calculateAttributes(self):
        
        self.balance = self.cleanDf['balance'].values
        self.dateAxis = self.cleanDf['date'].values
        self.transactions = self.cleanDf['sum'].values
        self.pdDates = [pd.to_datetime(str(date), format='%Y%m%d') for date in self.dateAxis]

        start = self.pdDates[0]
        end = self.pdDates[-1]
        self.pdRange = pd.date_range(start=start, end=end, periods=None, freq='D', )

    def separateTransactions(self):

        values, counts = np.unique(self.pdDates, return_counts=True)
        maxPerDay = max(counts)

        expenseXs, expenseYs = [], []
        incomeX, incomeY = [], []
        smallX, smallY = [], []

        for freq in range(1,max(counts)+1):
            for val, cnt in zip(values, counts):
                if cnt >= freq:
                    index = np.where(np.array(self.pdDates)==val)[0][freq-1]
                    if self.transactions[index] > 0:
                        incomeX.append(val)
                        incomeY.append(self.transactions[index])
                    else:
                        smallX.append(val)
                        smallY.append(-self.transactions[index])

            expenseXs.append(smallX)  
            expenseYs.append(smallY)  
            smallX, smallY = [], []

        self.expenseXs = expenseXs
        self.expenseYs = expenseYs
        self.incomeX = incomeX
        self.incomeY = incomeY
    
    def showPlots(self, cleanDf):
        self.cleanDf = cleanDf
        self.calculateAttributes()
        self.separateTransactions()
        
        self.createFigure()
        self.drawAxes()

        self.fig.canvas.mpl_connect('button_press_event', self.on_plot_hover) 
        self.fig.subplots_adjust(left=0.06, bottom=0.07, right=0.97, top=0.95)
        
        self.makeButtons()
        self.connectButtons()

        plt.show()



folder='matyi'
# folder='.'


files =[os.path.join(folder,file) for file in os.listdir(folder) if file.lower().endswith('csv')]

model = otpParser()
view = financeViewer()

myApp = Presenter(model, view, files)
myApp.showPlots()
