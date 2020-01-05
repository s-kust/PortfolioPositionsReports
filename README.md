# PortfolioPositionsReports

Python script that loads a list of portfolio positions from Google Spreadsheet, then for each position generates a report with charts and sends it to the email. 

How it works: 
1. Load a list of portfolio positions from Google Spreadsheet.
2. For each position, get the data from Yahoo Finance and generate a report with charts. 
3. Send every report to the specified email address in a separate letter. 

You can run the script in the cloud regularly at suitable intervals. For example, on business days in the morning and again one hour before the end of the trading time.

Reports currently look like this.
![Portfolio position report example](/misc/Portfolio-Position-Report-1.jpg)

Explanations:
* Adj Close - adjusted close price;
* SMA-200 - simple moving average 200 days;
* EMA-20 - exponential moving average 20 days;
* EMA-50 - exponential moving average 50 days;
* Upper Band - upper band of the Bollinger bands;
* ATR - average true range for the last 14 days. 

In the code, you can easily adjust the lookback periods of the moving averages or switch to a different set of indicators. 

The advantage of the script is that you can effortlessly change the set of items in the portfolio using your smartphone, as long as it works with Google Spreadsheets.

![Portfolio Spreadsheet](/misc/Porttfolio_Spreadsheet.jpg)

<h2>Preparing the script for work</h2>

Difficulties may arise at the stages of connecting to an SMTP server, planning the regular launch of the script on the remote Python hosting, as well as linking to the Google spreadsheet. These tasks are best solved sequentially, and not all together.

1. Fill the SMTP server settings in the script code in lines 123 or 126.
1. Indicate the sender on line 89, as well as the recipient's email on line 90,
1. For the initial testing of sending reports to your email, comment out the lines 141-150. Instead, use the basic diversified portfolio on line 136.
1. Load the script to the server and ensure that it works OK when launched manually.
1. Prepare the Google spreadsheet with the list of securities to be traced. To enable the script to work with that spreadsheet, follow [these instructions](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html). If the page is not available, use the [archived PDF version](misc/Google_Spreadsheets_Python.pdf).
   1. You'll have to go to the Google APIs Console, create a new project, enable API, etc. 
   1. You must give the script editing rights, not just viewing the spreadsheet, although in our case it does not perform any editing.
   1. The name of the JSON file must be **client_secret.json**. 
1. Delete the comments in lines 141-150, comment out line 136, and test the script in conjunction with the Google spreadsheet.
7. If everything works fine, schedule a regular run of the script.
