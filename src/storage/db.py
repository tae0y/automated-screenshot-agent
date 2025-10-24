
import psycopg
from contextlib import contextmanager
from src.config import PG_DSN

@contextmanager
def get_conn():
    with psycopg.connect(PG_DSN, autocommit=True) as conn:
        yield conn
