# deribit_client
Asynchronous client for Deribit exchange.

# About
The program takes data from the exchange for Bitcoin and Ethereum once a minute. Next, the data is added to the table 'last_price_currency'.
Another program creates an HTTP API server using the FastAPI library. Using requests, you can get data from the table at the last price of a currency, at all prices of a particular currency, 
at a price at a particular time (note that the time is specified in unix format).

# How to use
Before running the program you need:
1) Create a database in PostgraSQL. This can be done using a terminal or a windowed database application.
2) Indicate in the code your personal data and the name of the database for the program to connect to it. This needs to be done in 'main.py' and 'database_and_requests.py'
3) Create a table using the PostgreSQL.create_table function.
4) Run the uvicorn server in a terminal from the root folder. 
5) Run the 'database_and_requests.py' file.

After that, you can receive the necessary data via HTTP requests.






