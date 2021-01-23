# PortfolioPositionsReports

Python script that loads a list of stocks or ETF tickers from Google Spreadsheet, then for each position generates a report with charts and sends it to the email. You can effortlessly change the set of items in the watchlist using your smartphone, as long as it works with Google Spreadsheets. 

![Watchlist spreadsheet example](/misc/1.PNG)

How it works: 
1. Load a list of tickers from Google Spreadsheet.
2. For each ticker, get the data from Yahoo Finance and generate a report with charts. 
3. For each ticker or long-short spread, generate a report with charts and send it to the specified email address in a separate letter. 

You can run the script in the cloud regularly at suitable intervals. For example, on business days in the morning and again 15 minutes before the end of the trading time.

Reports currently look like this.
![Long-short spread report example](/misc/2.png)
and
![Ticker report example](/misc/3.png)

<h2>Preparing the script for work</h2>

Unfortunately, the initial setup of the script requires some skill. Difficulties may arise at the stages of connecting to an SMTP server, planning the regular launch of the script on the remote Python hosting, as well as linking to the Google spreadsheet. These tasks are best solved sequentially, and not all together.

1. Fill the SMTP server settings in the script code in lines 100 and 101.
1. Indicate the sender on line 67, as well as the recipient's email on line 68,
1. Prepare the Google spreadsheet with the list of tickers to be traced. To enable the script to work with that spreadsheet, follow [these instructions](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html). If the page is not available, use the [archived PDF version](misc/Google_Spreadsheets_Python.pdf).
   1. You'll have to go to the Google APIs Console, create a new project, enable API, etc. 
   1. You must give the script editing rights, not just viewing the spreadsheet, although in our case it does not perform any editing.
   1. The name of the JSON file must be **client_secret.json**. 
1. Load the script to the server and ensure that it works OK when launched manually.
1. If everything works fine, schedule a regular run of the script.
