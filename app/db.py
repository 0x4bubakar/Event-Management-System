import mysql.connector
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        print("Connection to DB successful!")

    except mysql.connector.Error as err:
        print(err)

    else:
        return conn