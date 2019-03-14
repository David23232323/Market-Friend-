Read me: Market Friend

Decription: 3 main features:
1. Analytics: a stock screener that returns stocks matching user desired parameters by filtering through all exisiting stocks.
Click on any of the returned stocks to see more information including a news briefing. 
2. Comparables: Find similar stocks to the user input stock by looping through all possible stocks and computing a similarity index.
 Also finds a target price by using regression from SK learn on the similar stocks.
3. Portfolio: Simulated portfolio that uses real time prices. Basically a real portfolio except with fake money. 

How to run:
Go into main.py and execute it as a script. 
Users will need to pip install: requests, json, sk learn, numpy, and iex finance

Side note: execute data.py to update information, don't have to do this every time as things stored in StockData.txt 
mostly change only quarterly (takes around 2 hours to update)

Shortcuts:
Press enter to search stocks instead of using the button. Use arrow keys to flip around returned stocks in analytics. 
