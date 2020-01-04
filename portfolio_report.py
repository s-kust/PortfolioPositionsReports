#!/usr/bin/python3.6

import datetime
import numpy as np
from scipy import stats
import pandas as pd
import pandas_datareader.data as web
import smtplib
import email
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates

# for getting the current portfolio items from the spreadsheet on your Google Drive
import gspread
from oauth2client.service_account import ServiceAccountCredentials
    
class StockDataReader:
    start_date = datetime.datetime.now() - datetime.timedelta(days=1.5*365)
#     start_date = '1-1-1995'
    
    ema_50 = lambda x: x.ewm(span=50).mean()
    ema_20 = lambda x: x.ewm(span=20).mean()
    
    # average true range
    def atr(df, n=14):
        data = df.copy()
        data['tr0'] = abs(data['High'] - data['Low'])
        data['tr1'] = abs(data['High'] - data['Close'].shift())
        data['tr2'] = abs(data['Low'] - data['Close'].shift())
        tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        atr = tr.ewm(alpha=1/n, min_periods=n).mean()
        return atr

    @classmethod
    def read_and_process(cls, symbol):
        res = web.DataReader(symbol, 'yahoo', cls.start_date)
        res['SMA-200'] = res['Adj Close'].rolling(200).mean()
        res['EMA-20'] = cls.ema_20(res['Adj Close'])
        res['EMA-50'] = cls.ema_50(res['Adj Close'])
        res['20 Day MA'] = res['Adj Close'].rolling(window=20).mean()
        res['20 Day STD'] = res['Adj Close'].rolling(window=20).std()
        res['Upper Band'] = res['20 Day MA'] + (res['20 Day STD'] * 2.2)
        res['Lower Band'] = res['20 Day MA'] - (res['20 Day STD'] * 2.2)
        res['ATR'] = cls.atr(res)
        res = res.drop(['High', 'Low', 'Open', 'Close', 'Volume'], axis=1) # delete unnecessary columns
        return (res)

def portfolio_item_report(symbol):
    res = StockDataReader.read_and_process(symbol)
    res1 = res[-66:]
    gs = gridspec.GridSpec(3,1)
    fig = plt.figure()
    ax1 = fig.add_subplot(gs[0])
    ax1.title.set_text(symbol + ' ' + 'Price and Moving Averages')
    res1['Adj Close'].plot(ax=ax1)
    res1['SMA-200'].plot(ax=ax1)
    res1['EMA-50'].plot(ax=ax1)
    res1['EMA-20'].plot(ax=ax1)
    ax1.legend(loc="upper left")
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.title.set_text(symbol + ' ' + 'Price and Bollinger Bands')
    res1['Adj Close'].plot(ax=ax2)
    res1['Upper Band'].plot(ax=ax2)
    res1['Lower Band'].plot(ax=ax2)
    ax2.legend(loc="upper left")
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.title.set_text(symbol + ' ' + 'Trailing Volatility')
    (res1['ATR']/res1['Adj Close']).plot(ax=ax3)
    ax3.xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().set_size_inches(12, 12)
    filename = symbol + '.png'
    plt.savefig(filename)
    # plt.show()

    df = res1.tail(2)
    df = df.drop(['20 Day MA', '20 Day STD', 'Lower Band'], axis=1)
    email_text = "{df}"
    email_text = email_text.format(df=df.to_html())

    # Send an HTML email with an embedded image and a plain text message for
    # email clients that don't want to display the HTML.

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage

    # Define these once; use them twice!
    strFrom = 'admin@endocrin-patient.com'
    strTo = 'send2kust@gmail.com'
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    subject = 'Portfolio: ' + symbol
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
    msgText = MIMEText(email_text + '<br><img src="cid:image1"><br>Have a nice day!', 'html')
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    fp = open(filename, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    # Send the email (this example assumes SMTP authentication is required)
    
    smtp = smtplib.SMTP_SSL('smtp1.your_provider.com', 465)
    
    # OR   
    # smtp = smtplib.SMTP('smtp.mail.ru', 465)
    # depemding on your SMTP provider
    
    smtp.connect('smtp1.your_provider.com')
    smtp.login('your@email', 'yourPassWord')
    
    smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    smtp.quit()
 
# for illustration, the simplest diversified portfolios - stocks and bonds
# symbols = ['SPY', 'AGG']
# not needed anymore, since the script gets 
# the current portfolio items from the spreadsheet on your Google Drive

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Portfolio").sheet1

symbols = sheet.col_values(1)

for symbol in symbols:
    print("Processing " + symbol)
    portfolio_item_report(symbol)
print('Reporting complete!')