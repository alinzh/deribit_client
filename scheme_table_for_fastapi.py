"""
Define scheme of `last_price_currency` table used in HTTP-request handlers from `main.py`.
"""

import sqlalchemy
from sqlalchemy import Column, Integer, String, BigInteger, Sequence

metadata = sqlalchemy.MetaData()

last_price_currency = sqlalchemy.Table(
    "last_price_currency",
    metadata,
    Column("id", Integer, Sequence("your_table_id_seq"), primary_key=True, autoincrement=True),  # TODO: undersrand what `your_table_id_seq` it is
    Column("ticker", String(50)),
    Column("last_price", Integer),
    Column("unix_time", BigInteger),
)
