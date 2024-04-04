from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import mysql
from fastapi import FastAPI, HTTPException, status
from modules.Users.users import UserCreate, UserLogin
import pandas as pd 
from jose import  jwt
from database import checks
from datetime import datetime, timedelta
app = FastAPI()
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# app.include_router(router_get_matchs.router, prefix="/api/v1/matchs")


@app.post('/sigup', response_model=UserCreate,status_code=status.HTTP_201_CREATED)
async def router_sigup_user(user: UserCreate):
    
    check = checks.Check()
    check.is_valid_email(user)
    check.is_valid_password(user)
    check.is_valid_phone_number(user)
    
    conn = mysql.MySql()
    conn.use_db('bet_rate')
    if conn.check_dupli_user_or_email(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tài khoản hoặc email đã tồn tại")
    
    table_name = 'users'
    df_user = user.dict()
    df_user =  pd.DataFrame([df_user])
    result = conn.push_data(table_name=table_name, df=df_user)
    conn.close()

    if result is not None:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Tạo tài khoản thành công")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tạo tài khoản không thành công")

ACCESS_TOKEN_SECRET = "cairocoders$§%§$Ednalan"
REFRESH_TOKEN_SECRET = "cairocoders$§%§$Ednalan"

def create_access_token(email: str) -> str:
    to_encode = {"email": email}
    expiry = datetime.utcnow() + timedelta(minutes=15)  
    to_encode.update({"exp": expiry})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(email: str) -> str:
    to_encode = {"email": email}
    expiry = datetime.utcnow() + timedelta(minutes=15)  
    to_encode.update({"exp": expiry})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm="HS256")
    return encoded_jwt

@app.post('/login')
async def login(user : UserLogin):
    conn = mysql.MySql()
    conn.use_db('bet_rate')
    result = conn.query(f"SELECT * FROM users WHERE email = '{user.email}';",show=False)
    print(result)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tài khoản không tồn tại")
    if result[0][1] != user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu không chính xác")
    
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    conn.close()
    return {"access_token": access_token, "refresh_token": refresh_token}

@app.post('/refresh-token')
async def refresh_token(refresh_token: str):
    try:
        decoded_token = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET, algorithms=["HS256"])
        email = decoded_token.get("email")
        if email:
            access_token = create_access_token(email)
            return {"access_token": access_token}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token không hợp lệ")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")

@app.get('/protected-route')
async def protected_route(token: str):
    try:
        decoded_token = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
        email = decoded_token.get("email")
        print(email)
        if email:
            return {"message": "mã token hợp lệ"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")
    
    
     