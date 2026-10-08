import os

from dotenv import load_dotenv
import psycopg

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg.connect(DATABASE_URL)


if __name__ == "__main__":
    connection = get_db_connection()
    print("PostgreSQL connection successful!")
    connection.close()