import sys
import pandas as pd
import numpy as np
import pandas_datareader.data as web
import plotly.graph_objects as go
import plotly.io as pio
import datetime
import time
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
# from IPython.core.debugger import set_trace
import mplfinance as mpf
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ATR - average true range

def atr(df, n=14):
        data = df.copy()
        data['tr0'] = abs(data['High'] - data['Low'])
        data['tr1'] = abs(data['High'] - data['Close'].shift())
        data['tr2'] = abs(data['Low'] - data['Close'].shift())
        tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        atr = tr.ewm(alpha=1/n, min_periods=n).mean()
        return atr
    
# the prices data is already imported, 
# now plot graphs and send them in emails
# these actions are repeated for every ticker, so they are designed as a function

def processSymbol (symbol1, symbol2=None, keywordTopic1='Portfolio:', keywordTopic2='Long'):
            
    # single ticker or long-short spread of two tickers?
    
    if (symbol2 is None):
        type='single'
        subject = keywordTopic1 + ' ' + keywordTopic2 + ' ' + symbol1
        filename = symbol1+'test'+'.png'
        plotTitle=symbol1+' Daily Price'
        plotType='ohlc'
        data = allTickersData[symbol1]
    else:
        type='spread'
        subject = 'Spread ' + symbol1 + ' ' + symbol2
        filename = symbol1+'_'+symbol2+'test'+'.png'
        plotTitle='Spread '+symbol1+'-'+symbol2+' Daily Price'
        plotType='line'
        data1 = allTickersData[symbol1] # long
        data2 = allTickersData[symbol2] # short
        data = data1/data2    
   
    mydpi = 100 # determined by trial and error
    if (type=='single'):
        res1 = data.tail(50)
        atr_plot = mpf.make_addplot(res1['ATR'], panel=2, ylabel='ATR')
        mpf.plot(res1, type=plotType, style='yahoo', addplot=atr_plot, \
             title=plotTitle, volume=True, figsize =(794/mydpi,512/mydpi), savefig=filename)
    else:
        res1 = data.tail(350)
        mpf.plot(res1, type=plotType, style='yahoo', \
             title=plotTitle, figsize =(794/mydpi,512/mydpi), savefig=filename)

    strFrom = 'send_from@example.com'
    strTo = 'send_to@example.com'
    
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = strFrom
    msgRoot['To'] = strTo
    msgRoot.preamble = 'This is a multi-part message in MIME format, with picture.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message, do you see the picture?')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    # msgText = MIMEText('Some <i>HTML</i> text and USMV image.<br><img src="cid:image1"><br>Have a nice day', 'html')
    msgText = MIMEText('<img src="cid:image1"><br>Have a nice day!', 'html')
    msgAlternative.attach(msgText)
    # This code assumes the image is in the current directory
    fp = open(filename, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    if os.path.exists(filename):
        os.remove(filename)

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    smtp = smtplib.SMTP_SSL('smtp1.your_provider.com', 465)
    smtp.connect('smtp1.your_provider.com')
    smtp.login('send_from@example.com', 'pAsswo2rd')   
    smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    smtp.quit()

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Portfolio")

sheet_instance1 = sheet.get_worksheet(0)
ideas = pd.DataFrame.from_dict(sheet_instance1.get_all_records())
ideas = ideas.applymap(lambda x: x.strip() if isinstance(x, str) else x)
ideas.replace('', np.nan, inplace=True)
longs = ideas['Long'].dropna()
shorts = ideas['Short'].dropna()
spreads = ideas[['SpreadLong', 'SpreadShort']].dropna()
allTickers=[]
allTickers.extend(longs.values.tolist())
allTickers.extend(shorts.values.tolist())
allTickers.extend(spreads['SpreadLong'].values.tolist())
allTickers.extend(spreads['SpreadShort'].values.tolist())
allTickers = set(allTickers) # remove duplicates, for not to import the same tiker data several times

print(allTickers)

# for long-short spreads, we use the last 1.5 years data
start_date = datetime.datetime.now() - datetime.timedelta(days=1.5*365) 
allTickersData = {}

# first, import all the required tickers data from Yahoo! Finance
for ticker in allTickers:
    print('Importing data', ticker, '...')
    time.sleep(1)
    imported = web.DataReader(ticker, 'yahoo', start_date)
    imported['ATR_100'] = atr(imported, 100)
    imported['ATR_6'] = atr(imported, 6)
    imported['ATR'] = imported['ATR_6']/imported['ATR_100'] 
    allTickersData.update({ticker : imported})

# then, plot charts and send e-mails
for ticker in longs:
    print('Processing Long', ticker)
    time.sleep(0.5)
    processSymbol(ticker, keywordTopic1='Idea:', keywordTopic2='Long')
for ticker in shorts:
    print('Processing Short', ticker)
    time.sleep(0.5)
    processSymbol(ticker, keywordTopic1='Idea:', keywordTopic2='Short')
for index, row in spreads.iterrows():
    time.sleep(0.5)
    print('Processing Spread', row['SpreadLong'], row['SpreadShort'])
    processSymbol(row['SpreadLong'], row['SpreadShort'])
print('Daiy reporting complete!')
