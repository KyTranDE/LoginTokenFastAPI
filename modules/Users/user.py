import os
from dotenv import load_dotenv
# from database import mysql
from jose import  jwt
from database import postgre

dotenv_path = '.env'
load_dotenv(dotenv_path)

ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
ALGORITHM = os.getenv('ALGORITHM')


def get_data(name:str,data : str)->str:
    conn = postgre.PostgresTool(postgre.HOST, postgre.USER, postgre.PORT, postgre.PASSWORD,postgre.DATABASE)
    result = conn.query(f"SELECT * FROM dim_user WHERE {name} = '{data}';",show=False)
    conn.close()
    return result

def validate_user(token: str):
    decoded_token = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=ALGORITHM)
    result = get_data('email',decoded_token.get('email'))
    return result