"""
This file contains the RequestDerebit class, the PostgreSQL class, and the LastPriceCurrency class.

RequestDerebit is an asynchronous client. Every minute he makes requests to the Deribit exchange and
takes the value of Bitcoin and Ether.

PostgreSQL class whose methods are also asynchronous. It adds the data received from the exchange to the table.

"""
import asyncio
import json

import asyncpg
import websockets
from sqlalchemy import Column, Integer, String, BigInteger, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, List

Base = declarative_base()


class RequestDerebit:
    """Class for get data from exchange."""

    def __init__(self):
        self.message_btc = {
            "jsonrpc": "2.0",
            "id": 8106,
            "method": "public/ticker",
            "params": {
                "instrument_name": "BTC-PERPETUAL",
            }
        }
        self.message_eth = {
            "jsonrpc": "2.0",
            "id": 8107,
            "method": "public/ticker",
            "params": {
                "instrument_name": "ETH-PERPETUAL",
            }
        }
        self.sql = PostgreSQL(
            db_name="deribit_client", db_host="localhost", db_user="postgres", db_pass="<PASSWORD>", db_port=5432,
        )

    async def request(self, message: dict) -> Dict:
        """
        Doing request to exchange and getting data about last price from it.
        message: contains data for request
        """
        async with websockets.connect("wss://test.deribit.com/ws/api/v2/public/ticker") as websocket:
            await websocket.send(json.dumps(message))
            while websocket.open:
                response = await websocket.recv()
                data = json.loads(response)
                if "result" in data:
                    return data
                else:
                    print(f'Response: {response}')

    async def add_data_to_table(self, data: dict):
        """Add response from request to table last_price_currency."""
        last_price = data["result"]["last_price"]
        unix_time = data["result"]["timestamp"]
        ticker = data["result"]["instrument_name"]
        await self.sql.add_last_price_to_table(ticker, last_price, unix_time)
        print(f'Price {data["result"]["instrument_name"]}: {last_price}')

    async def run_client(self, message: dict):
        """
        Call func `request` and func `add_data_to_table` each  60 sec.
        message: dict with request to server.
        """
        while True:
            # Use try/except for avoid an error due to a bad connection to the exchange.
            try:
                data = await self.request(message)
                if data is not None:
                    await self.add_data_to_table(data)
                await asyncio.sleep(60)
            except ConnectionError:
                continue

    async def create_tasks(self):
        """Create tasks, which will make requests and add data to table."""
        tasks = [
            asyncio.create_task(self.run_client(self.message_btc)),
            asyncio.create_task(self.run_client(self.message_eth))
        ]
        await asyncio.wait(tasks)


# Create declarative class.
# It allows to create tables more conveniently:
# just list the table structure inside the class that is inherited from `Base`.
class LastPriceCurrency(Base):
    __tablename__ = "last_price_currency"

    # id will be created automatically
    id = Column(Integer, Sequence("your_table_id_seq"), primary_key=True, autoincrement=True)  # TODO: undersrand what `your_table_id_seq` it is
    ticker = Column(String(50))
    last_price = Column(Integer)
    unix_time = Column(BigInteger)


class PostgreSQL:
    """
    Class for work with database, consist func for create db and tables, for add date to table.
    Before use need to add your personal data - `db_name`, `db_host`, `db_user`, `db_pass`, `db_port`.
    """

    def __init__(self, db_name, db_host, db_user, db_pass, db_port):
        # virtual machine for async connection
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}", echo=True,
        )
        self.db_name = db_name
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def create_db(self):
        """Create db, if not exists."""
        conn = await asyncpg.connect(
            host=self.engine.url.host,
            port=self.engine.url.port,
            user=self.engine.url.username,
            password=self.engine.url.password
        )
        await conn.execute(f"CREATE DATABASE {self.db_name}")
        await conn.close()
        print("Deribit_client database successfully created")

    async def create_table(self):
        """Create table, if not exists."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Last_price_currency table successfully created")

    async def add_last_price_to_table(self, ticker: str, last_price: int, unix_time: int):
        """
        Func adds response (ticker, last price of currency, time in unix format) from exchange to table.
        `id` is created in the table by default (see `LastPriceCurrency`).
        ticker: currency name, for example: 'ETH-PERPETUAL'
        last_price: the price of the currency on the exchange at the time of the request
        unix_time: the exact date and time the request was made (in unix format)
        """
        async with self.session_factory() as session:
            async with session.begin():
                input_data = LastPriceCurrency(ticker=ticker, last_price=last_price, unix_time=unix_time)
                session.add(input_data)
            print(f"Added data to last_price_currency table: {ticker}, {last_price}, {unix_time}")


async def main():
    rd = RequestDerebit()
    await rd.create_tasks()


if __name__ == "__main__":
    asyncio.run(main())
