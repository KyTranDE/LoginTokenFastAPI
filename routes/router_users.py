from fastapi import Depends,Header,APIRouter,HTTPException,HTTPException, status
from modules.Users.interface import UserCreate, UserLogin
import pandas as pd 
from jose import  jwt
from database import checks
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import hashlib
from database import postgre
import os
from dotenv import load_dotenv
from modules.Users.user import validate_user, get_data
from datetime import date
from publisher import publish_message
dotenv_path = '.env'
load_dotenv(dotenv_path)

router = APIRouter()
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
ALGORITHM = os.getenv('ALGORITHM')
# ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def create_access_token(email: str) -> str:
    to_encode = {"email": email}
    # expiry = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))  
    # to_encode.update({"exp": expiry})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm=ALGORITHM)
    return encoded_jwt



@router.post('/sigup', response_model=UserCreate,status_code=status.HTTP_201_CREATED)
async def router_sigup_user(user: UserCreate):
    
    check = checks.Check()
    check.is_valid_email(user)
    # check.is_valid_password(user)
    # check.is_valid_phone_number(user)
    
    conn = postgre.PostgresTool(postgre.HOST, postgre.USER, postgre.PORT, postgre.PASSWORD,postgre.DATABASE)
    if get_data('email',user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The account or email already exists")
    user.password = hash_password(user.password)

    df_user = pd.DataFrame([user.dict()])
    # Đặt giá trị mặc định cho date_create và day_expired nếu không được cung cấp
    if 'date_create' not in df_user or pd.isna(df_user['date_create']).all():
        df_user['date_create'] = date.today()
    if 'day_expired' not in df_user or pd.isna(df_user['day_expired']).all():
        df_user['day_expired'] = datetime.now() + timedelta(days=30)

    result = conn.push_data(table_name='dim_user', df=df_user)
    conn.close()

    if result is not None:
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Account created successfully")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account creation unsuccessful")




@router.post('/login')
async def login(user: UserLogin):
    result = get_data('email', user.email)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The account does not exist")
    if result[0][2] != hash_password(user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    
    day_expired = result[0][8]
    if day_expired < datetime.now():
        publish_message('expired_accounts', {'email': user.email, 'expired_at': str(day_expired)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The account has expired")
    
    return {"email": user.email, "token": create_access_token(user.email)}

@router.get('/me')
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        result = validate_user(token)
        if not result:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"email": result[0][1], "first_name": result[0][5], "last_name": result[0][6], "day_expired": result[0][8]}
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")