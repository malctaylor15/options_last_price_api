Option Price function for Google sheets

Made a function to get option prices from yahoo and pull them into google sheets 

Some steps... 

1. Install dependencies like yfinance and uvicorn 
In the terminal run 

pip install -r requirements.txt

2. Test locally in the run_server notebook 
That will run it in a notebook. To shut it off, you should restart the whole notebook 
If you're deploying locally, remember to change the HOST TO 127.0.0.1 if in production, we can use 0.0.0.0

3. Play around with keys and different options...  127.0.0.1:9000/docs for the UI version 
Remember to double check it on a site like https://finance.yahoo.com/quote/TSLA/options/?date=1766102400

4. In the google sheet, you'll need to go to extensions, app script and copy the google_sheets_script.gs to the app script folder.    


We can check some of the endpoints at  
http://dev.malctaylor15.com:9000/docs 



## Advanced Management

### Editing the Service
Because we used a **symbolic link**, you can edit `fastapi_finance.service` in this directory directly. After saving changes, run:
`sudo systemctl daemon-reload && sudo systemctl restart fastapi_finance`

### Fail-Safe (Anti-Crash Loop)
The service is configured to give up if it crashes 5 times within 5 minutes. This prevents the API from spamming the system if there is a major code error (like a missing API key).

### Resetting a "Failed" State
If the service hits the "Burst Limit" and stops trying to restart, it will enter a `failed` state. To clear this and try again:
`sudo systemctl reset-failed fastapi_finance`
`sudo systemctl start fastapi_finance`