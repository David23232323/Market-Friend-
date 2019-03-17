from Button import *
import math 
import numpy as np
import sklearn as sk
from sklearn.model_selection import train_test_split
from sklearn import linear_model
import requests
import json
from iexfinance import Stock

#This page gives the comparable stocks and uses linear regression to 
#arrive at a estimated value based on the stock's peers

def predict(data): #sk learn regression
    index = getAvailableComparisons(data)
    X = getX(data, index)
    X = np.array(X) #X Corresponds to particular stocks
    y = getY(data)  #y Corresponds to price of stocks 
    y = np.array(y)
    reg = sk.linear_model.LinearRegression().fit(X, y)
    subject = getSubject(data, index) 
    predictValue = reg.predict(np.array([subject]))
    stockName = 0 
    stockPrice = 1 
    data.predictedDifference = predictValue[stockName] - data.selectedInfo[stockPrice] 
    if data.predictedDifference < 0:
        data.loss = True 
        data.predictedValue = data.selectedInfo[1] - \
        (data.selectedInfo[1] - predictValue[0])**0.5
    else:
        data.loss = False  
        data.predictedValue = data.selectedInfo[1] + \
        (predictValue[0] - data.selectedInfo[1])**0.5
    data.percentChange = ((data.predictedValue - data.selectedInfo[1])/data.selectedInfo[1])*100
    data.predicted = True 

    
def getSubject(data, index):
    value = []
    for i in index:
        value.append(data.selectedInfo[i])
    return value 
    
def getX(data, index): #filters data
    value = []
    for stock in data.similarStocks:
        individual = []
        for i in index:
            individual.append(stock[i])
        value.append(individual)
    return value 
    
def getY(data): #filters data
    values = []
    for stock in data.similarStocks:
        values.append(stock[1])
    return values
    
def getAvailableComparisons(data):
    index = []
    for i in range(2,len(data.selectedInfo)):
        if i == 3: #sector
            continue 
        elif validIndex(data, i):
            index.append(i)
    return index 
    
def validIndex(data, i): #checks if applicable to all stocks
    if data.selectedInfo[i] == 0 or data.selectedInfo[i] == None:
        return False 
    for stock in data.similarStocks:
        if stock[i] == 0 or stock[i] == None:
            return False
    return True 
            
def searched(data):
    for stock in data.stockScreenerInfo:
        if stock[0].lower() == data.stockTicker.lower():
            data.selectedInfo = stock
            data.selectedInfo[1] = Stock(data.selectedInfo[0]).get_price()
            return None 
            
def compare(data): #similarity alogritihm  
    data.resultLst = []
    checkIndex = [(2,0.3), (4,0.3), (8,0.05), (9,0.05), (12, 0.05), (13, 0.05),
     (15,0.1), (16,0.1)] #Weightings to  PE, market cap, ROA, revenue, cash, 
                         #debt, roc, P/b
    sector = 3
    for stockMetrics in data.stockScreenerInfo:
        if data.selectedInfo[sector] != stockMetrics[sector] :
            continue
        statistic = 0 #difference statistics
        for i in checkIndex:
            weighting = i[1]
            if data.selectedInfo[i[0]] != 0 and data.selectedInfo[i[0]] != None:
                if stockMetrics[i[0]] != 0 and stockMetrics[i[0]] != None:
                    statistic += (difference(data.selectedInfo[i[0]], 
                    stockMetrics[i[0]]))*weighting
                else:
                    statistic += 2*weighting
        stockInfo = stockMetrics.append(statistic)
        binaryInsertionSort(stockMetrics, data) #resultLst.append(stockMetrics)
    data.similarStocks = []#top 5 similar, first one is itself
    for i in range(1,6):
        data.similarStocks.append(data.resultLst[i])
        
def binaryInsertionSort(element, data): #ranks stocks based on similarity 
    min = 0
    if  len(data.resultLst) == 0:
       data.resultLst.insert(min, element)
       return 
    max = len(data.resultLst) 
    mid = (max - 1)//2
    while data.resultLst[mid][-1] != element[-1]:
        if data.resultLst[mid][-1] > element[-1]:
            max = mid
            mid = (min + max)//2 
            if mid == max:
                data.resultLst.insert(mid, element)
                return 
        else:
            min = mid
            mid = (min + max)//2
            if mid == min:
                data.resultLst.insert(mid+1, element)
                return
    data.resultLst.insert(mid, element)
    
        
def difference(a, b):
    a = abs(a)
    b = abs(b)
    return (max(a,b))/(min(a,b))
    
    
def drawMlScreen(canvas, data):
    canvas.create_image(0, 0, anchor=NW, image=data.purpleBackground)
    canvas.create_text(data.width//2, 50, 
    text = "Comparatives With Machine Learning!!", font = "Times 20 bold")
    data.menu = mainMenu("Menu", data.width//10, data.height//20, 20, 10, "ef")
    data.menu.draw(canvas)
    data.inputButtonML.draw(canvas, data, "grey")
    
    #Quantity 
    data.searchButton.draw(canvas)
    
    #add stock button 
    data.filterButton.draw(canvas)
    
    if data.searched:
        drawSearched(canvas, data)
    else:
        canvas.create_text(500, 100, text = "Please enter a valid stock ticker")
        drawEmpty(canvas, data)
    
    if data.searched and data.similarStocksCompared:
        drawSimilarStocks(canvas, data)
    
    if data.similarStocksCompared and data.predicted:
        canvas.create_text(data.width//2, 450, text = data.stockTicker.upper(), 
        font = "Times 18")
        if data.loss:
            color = "red"
            canvas.create_text(150, 500, 
            text = "Current Price: %0.2f"%data.selectedInfo[1], font = "Times 15")
            canvas.create_text(150, 550, 
            text = "Target Price: %0.2f" %data.predictedValue, font = "Times 15")
            canvas.create_text(600, 500, 
            text = "Expected Downside: -%0.2f" %(abs(data.predictedDifference)**0.5), 
            font = "Times 15", fill = color)
            canvas.create_text(600, 550, 
            text = "Percent Loss: %0.2f" %data.percentChange + "%", 
            font = "Times 15", fill = color)
        else:
            color = "green"
            canvas.create_text(150, 500, 
            text = "Current Price: %0.2f"%data.selectedInfo[1],
             font = "Times 15")
            canvas.create_text(150, 550, 
            text = "Target Price: %0.2f"%data.predictedValue, 
            font = "Times 15", fill = color)
            canvas.create_text(600, 500, 
            text = "Expected Upside: %0.2f" %(abs(data.predictedDifference)**0.5), 
            font = "Times 15", fill = color)
            canvas.create_text(600, 550, 
            text = "Percent Growth: %0.2f" %data.percentChange + "%", 
            font = "Times 15", fill = color)
    else:
        canvas.create_text(150, 500, text = "Current Price:", font = "Times 15")
        canvas.create_text(150, 550, text = "Target Price:", font = "Times 15")
        canvas.create_text(600, 500, text = "Upside/Downside:", font = "Times 15")
        canvas.create_text(600, 550, text = "Percent Growth:", font = "Times 15")
        drawEmptyBoxes(canvas, data)
        
def drawEmptyBoxes(canvas,data): #borders
    canvas.create_text(data.width//2, 450, text = data.stockTicker.upper(),
            font = "Times 18") 
    label = ["Ticker", "Price", "P/E", "Sector", "Market Cap", "ROA", 
    "Revenue", "Cash", "Debt", "Roc", "P/B"]
    x = 20
    y = 250
    width = 70
    height = 30
    for i in range(11):
        canvas.create_rectangle(x +width*i,y, x + width*(i+1), y + height)
        canvas.create_text((x +width*i+x + width*(i+1))/2, y+height/2,
         text = label[i])
        canvas.create_rectangle(x +width*i,y+30, x + width*(i+1), y + 30+height)
        for j in range(5):
            canvas.create_rectangle(x +width*i,y+30*j, x + width*(i+1), 
            y + height+30*(j+1))
        
def drawEmpty(canvas, data): #second table 
    label = ["Ticker", "Price", "P/E", "Sector", "Market Cap", "ROA", 
    "Revenue", "Cash", "Debt", "Roc", "P/B"]
    x = 20
    y = 150
    width = 70
    height = 30 
    for i in range(11):
        canvas.create_rectangle(x +width*i,y, x + width*(i+1), y + height)
        canvas.create_text((x +width*i+x + width*(i+1))/2, y+height/2, text = label[i])

   
def drawSimilarStocks(canvas, data): 
    label = ["Ticker","Price", "P/E", "Sector", "Market Cap", "ROA", "Revenue", 
    "Cash", "Debt", "Roc", "P/B"]
    index = [0,1,2,3,4,8,9,12,13,15,16]
    x = 20
    y = 250
    width = 70
    height = 30 
    canvas.create_text(data.width//2, 230, text = "Similar Stocks", 
    font = "Times 18")
    for i in range(len(label)):
        canvas.create_rectangle(x +width*i,y, x + width*(i+1), y + height)
        canvas.create_text((x +width*i+x + width*(i+1))/2, y+height/2, text = label[i])
        for j in range(5):
            value = data.similarStocks[j][index[i]]
            if str(value).isnumeric():
                if len(str(value//1)) >= 9:
                    value = value//1000000
                    value = str(value) + "M"
            elif isinstance(value, float):
                value = "%0.3f" %value
            elif i == 3:
                modified = ""
                for letter in value:
                    if letter.isspace():
                        modified += "\n"
                    else:
                        modified += letter 
                canvas.create_rectangle(x +width*i,y+30+30*j, x + width*(i+1), 
                y + height+30*(j+1))
                canvas.create_text((x +width*i+x + width*(i+1))/2, 
                y+height/2+30+30*j, text = modified,
                font = "Times 8")
                continue 
            canvas.create_rectangle(x +width*i,y+30*j, x + width*(i+1), 
            y + height+30*(j+1))
            canvas.create_text((x +width*i+x + width*(i+1))/2,
             y+height/2+30+30*j, text = value)
    
def drawSearched(canvas, data):
    #Price, PE, market cap, ROA, revenue, cash, debt, roc, P/b
    #draw single table data.selectedInfo
    label = ["Ticker", "Price", "P/E", "Sector", "Market Cap", "ROA", 
    "Revenue", "Cash", "Debt", "Roc", "P/B"]
    
    index = [0,1,2,3,4,8,9,12,13,15,16]

    stockInfo = data.selectedInfo
    x = 20
    y = 150
    width = 70
    height = 30 
    for i in range(len(index)):
        value = stockInfo[index[i]]
       
        if str(value).isnumeric():
            if len(str(value//1)) >= 9:
                value = value//1000000
                value = str(value) + "M"
        elif isinstance(value, float):
            value = "%0.3f" %value
        elif i == 3:
            modified = ""
            for letter in value:
                if letter.isspace():
                    modified += "\n"
                else:
                    modified += letter 
            canvas.create_rectangle(x +width*i,y, x + width*(i+1), 
            y + height)
            canvas.create_text((x +width*i+x + width*(i+1))/2, y+height/2, 
            text = label[i])
            canvas.create_rectangle(x +width*i,y+30, x + width*(i+1), 
            y + height+30)
            canvas.create_text((x +width*i+x + width*(i+1))/2, y+height/2+30, 
            text = "%s" %modified, 
        font = "Times 8")
            continue     
        canvas.create_rectangle(x +width*i,y, x + width*(i+1), y + height)
        canvas.create_text((x +width*i+x + width*(i+1))/2, y+height/2,
         text = label[i])
        canvas.create_rectangle(x +width*i,y+30, x + width*(i+1), y + height+30)
        canvas.create_text((x +width*i+x + width*(i+1))/2, y+height/2+30, 
        text = "%s" %value)
    #draw ML info 
    
def keyMlScreen(event, data):
    #work on fixing clicking in and out of the box 
    if event.keysym == "Return":
        try:
            searched(data)
            data.searched = True
        except:
            data.stockTicker = ""
            data.searched = False 
    elif event.char.isalpha():
        if len(data.stockTicker) < 6:
            data.stockTicker += event.char
    elif event.keysym == "BackSpace" and len(data.stockTicker) > 0:
        data.stockTicker = data.stockTicker[:-1]

    
def mouseMlScreen(event, data):
    if data.menu.clickedButton(event.x, event.y):
            data.startScreen = True
            data.analyticsMenu = False
            data.stockScreener = False
            data.portfolioScreen = False 
            data.mlScreen = False
            data.stockTicker = ""
    elif data.searchButton.clickedButton(event.x, event.y):
        try:
            searched(data)
            data.searched = True
        except:
            data.stockTicker = ""
            data.searched = False 
    elif data.filterButton.clickedButton(event.x, event.y):
        data.similarStocksCompared = True 
        if data.searched:
            compare(data)
            predict(data)
    elif data.inputButtonML.clickedButton(event.x, event.y):
        data.inputButtonML.clicked = True 
    else: 
        data.inputButton.clicked = False 
        data.stockTicker = ""
        
