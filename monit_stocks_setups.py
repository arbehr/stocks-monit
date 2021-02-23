from urllib.request import urlopen
import json
import time
import datetime

TIME_WINDOW_IN_DAYS = 5 #days
API_KEY = 'put your alphavantage key here'

class Candle:
  def __init__(self, open, high, low, close, volume):
    self.open = open
    self.high = high
    self.low = low
    self.close = close
    self.volume = volume

class BollingerBand:
  def __init__(self, middle, lower, upper):
    self.middle = middle
    self.lower = lower
    self.upper = upper

class Stock:
  def __init__(self, name):
    self.name = name
    # Analyse main trend according mm20
    self.timeWindowBB = self.getDailyBB()
    self.deltaMME20 = self.getDeltaMM20()
    self.trendMME20 = self.isMMEgrowingForTimeWindow(self.deltaMME20)

    # Just working with positive trend
    if(self.trendMME20):
      self.timeWindowMME9 = self.getDailyMME9()
      self.timeWindowDailyCandle = self.getDailyCandles()
      self.deltaMME9 = self.getDeltaMME9()
      self.trendMME9 = self.isMMEgrowingForTimeWindow(self.deltaMME9)

  def getDeltaMM20(self):
    mme20_array = []
    for i in range(0, TIME_WINDOW_IN_DAYS-1):
        mme20_array += [self.timeWindowBB[i].middle > self.timeWindowBB[i+1].middle and +1 or -1]

    return mme20_array

  def getDeltaMME9(self):
    mme9_array = []
    for i in range(0, TIME_WINDOW_IN_DAYS-1):
        mme9_array += [self.timeWindowMME9[i] > self.timeWindowMME9[i+1] and +1 or -1]
    return mme9_array
  
  def isMMEgrowingForTimeWindow(self, timeWindowDeltaMME):
    for i in range(0, TIME_WINDOW_IN_DAYS-3):
        if(timeWindowDeltaMME[i] < timeWindowDeltaMME[i+1]):
            return 0
    return 1

  def isMME9reversing(self):
    if(self.timeWindowMME9[0] <= 0):
        return 0
    for i in range(1, TIME_WINDOW_IN_DAYS-2):
        if(self.timeWindowMME9[i] == 1):
            return 0
    return 1

  def getDailyMME9(self):
    mme9_array = []
    url = ('https://www.alphavantage.co/query?function=EMA&symbol=' +
        self.name+'.SA&interval=daily&time_period=9&series_type=close&apikey=' + API_KEY)
    response = urlopen(url)

    string = response.read().decode('utf-8')
    json_obj = json.loads(string)

    try:
      for i in range(0, TIME_WINDOW_IN_DAYS):
        previousDate = currentDay - datetime.timedelta(days=i)
        previousDateFormatted = previousDate.strftime ('%Y-%m-%d')
        mme9_array += [float(json_obj['Technical Analysis: EMA'][previousDateFormatted]['EMA'])]
    except KeyError:
      print('Erro de key para MM9E: ' + str(i))
    return mme9_array

  def getDailyBB(self):
    stockDailyBBArray = []
    url = ('https://www.alphavantage.co/query?function=BBANDS&symbol=' +
        self.name + '.SA&interval=daily&time_period=21&series_type=close&nbdevup=1.8&nbdevdn=1.8&apikey=' + 
        API_KEY)
    response = urlopen(url)

    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
  
    try:
      for i in range(0, TIME_WINDOW_IN_DAYS):
        previousDate = currentDay - datetime.timedelta(days=i)
        previousDateFormatted = previousDate.strftime ('%Y-%m-%d')

        bollingerBand = BollingerBand(
          json_obj['Technical Analysis: BBANDS'][previousDateFormatted]['Real Middle Band'],
          json_obj['Technical Analysis: BBANDS'][previousDateFormatted]['Real Lower Band'],
          json_obj['Technical Analysis: BBANDS'][previousDateFormatted]['Real Upper Band'])
        stockDailyBBArray += [bollingerBand]

    except:
      bollingerBand = BollingerBand(0,0,0)
      stockDailyBBArray += [bollingerBand]
    return stockDailyBBArray     

  def getDailyCandles(self):
    stockDailyCandlesArray = []
    url = ('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' +
        self.name+'.SA&apikey=' + API_KEY)
    response = urlopen(url)

    string = response.read().decode('utf-8')
    json_obj = json.loads(string)

    try:
      for i in range(0, TIME_WINDOW_IN_DAYS):
        previousDate = currentDay - datetime.timedelta(days=i)
        previousDateFormatted = previousDate.strftime ('%Y-%m-%d')

        candle = Candle( 
          json_obj['Time Series (Daily)'][previousDateFormatted]['1. open'],
          json_obj['Time Series (Daily)'][previousDateFormatted]['2. high'],
          json_obj['Time Series (Daily)'][previousDateFormatted]['3. low'],
          json_obj['Time Series (Daily)'][previousDateFormatted]['5. adjusted close'],
          json_obj['Time Series (Daily)'][previousDateFormatted]['6. volume'])
        stockDailyCandlesArray += [candle]

    except KeyError:
      candle = Candle(0,0,0,0,0)
      stockDailyCandlesArray += [candle]
    return stockDailyCandlesArray

print('Starting stocks analysis...')
currentDay = datetime.datetime.strptime('2021-02-05', '%Y-%m-%d')

stock = Stock('PETR4')

print('=========================')
print("Report for " + stock.name)

if(stock.trendMME20):
  print("Positive trend")
else:
  print("Negative trend, skipping")
