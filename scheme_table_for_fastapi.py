"""
Define scheme of `last_price_currency` table used in HTTP-request handlers from `main.py`.
"""

import sqlalchemy
from sqlalchemy import Column, Integer, String, BigInteger

metadata = sqlalchemy.MetaData()

last_price_currency = sqlalchemy.Table(
    "last_price_currency",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ticker", String(50)),
    Column("last_price", Integer),
    Column("unix_time", BigInteger),
)
