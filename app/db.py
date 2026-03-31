from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

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


def create_user(username, plain_text_password):
    hashed_password = generate_password_hash(plain_text_password)

def verify_login(username, provided_password):

    return check_password_hash(db_hashed_pw, provided_password)