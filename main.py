"""
Run ASGI-server in console from the repository root with following code:

`uvicorn main:app --reload`

Then you can make requests by:
* To get all data by specific ticker:  `http://127.0.0.1:8000/all_data?ticker_filter=TICKER`
* To get last price: `http://127.0.0.1:8000/last_price?ticker_filter=TICKER`
* To get price on data: `http://127.0.0.1:8000/price_by_unix_date?ticker_filter=TICKER&unix_time=UNIX_TIME`
"""

import databases
import sqlalchemy
from fastapi import FastAPI
from typing import Dict, List

from scheme_table_for_fastapi import last_price_currency

# Here you need to add your user_name, password, host, name_of_database
db_user = '<USER_NAME>'
db_password = '<PASSWORD>'
db_host = 'localhost'
db_port = 5432
db_name = 'deribit_client'
sqlalchemy_database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

database = databases.Database(sqlalchemy_database_url)
app = FastAPI()


@app.on_event("startup")
async def startup():
    """Connect to db on the app launch."""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Disconnect from db on the app stop."""
    await database.disconnect()


@app.get("/all_data")
async def get_all_data_by_ticker(ticker_filter: str) -> List:
    """
    Method returns all data from table `last_price_currency` by specified ticker:
    `ticker`, `last_price` and `unix_time`.
    By default, link is http://127.0.0.1:8000/all_data?ticker_filter=TICKER.
    ticker_filter: ticker of currency, for example BTC-PERPETUAL.
    return: all saved data by that ticker.
    """
    query = (
        sqlalchemy.select(
            [
                last_price_currency.c.ticker,
                last_price_currency.c.last_price,
                last_price_currency.c.unix_time,
            ]
        )
        .select_from(last_price_currency)
        .where(last_price_currency.c.ticker == ticker_filter)
    )
    result = await database.fetch_all(query)
    return result


@app.get("/last_price")
async def get_last_price_by_ticker(ticker_filter: str) -> Dict:
    """
    Method returns just one value - last price of ticker which will you choose.
    Link by default is http://127.0.0.1:8000/last_price?ticker_filter=TICKER.
    ticker_filter: ticker of currency, for ex BTC-PERPETUAL.
    return: last price for that ticker.
    """
    query = (
        sqlalchemy.select(
            [
                last_price_currency.c.last_price,
            ]
        )
        .select_from(last_price_currency)
        .where(last_price_currency.c.ticker == ticker_filter)
        # sorted data by unix_time in descending order
        .order_by(sqlalchemy.desc(last_price_currency.c.unix_time))
    )
    result = await database.fetch_all(query)
    if result:
        # get just last price
        last_price = result[0]
        return {"last_price": last_price}
    else:
        return {"error": "Ticker not found"}


@app.get("/price_by_unix_date")
async def get_price_of_currency_by_data(ticker_filter: str, unix_time: int) -> List:
    """
    Method returns price of ticker for specific date.
    ticker_filter: ticker of currency, for ex. BTC-PERPETUAL.
    unix_time: is date in unix format.
    return: price of ticker in specific date.
    """
    query = (
        sqlalchemy.select(
            [
                last_price_currency.c.ticker,
                last_price_currency.c.last_price,
                last_price_currency.c.unix_time,
            ]
        )
        .select_from(last_price_currency)
        .where(last_price_currency.c.ticker == ticker_filter)
        .where(last_price_currency.c.unix_time == unix_time)
    )
    result = await database.fetch_all(query)
    if result:
        return result
    else:
        return {"error": "Price for that date not found."}
