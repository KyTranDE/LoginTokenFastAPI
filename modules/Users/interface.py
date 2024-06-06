from typing import Union
from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta


from typing import Optional

class UserCreate(BaseModel):
    email: str 
    password: str
    phone_number: str
    date_create: date = Field(default_factory=date.today)
    first_name : str
    last_name : str
    role : str
    status : bool
    day_expired: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=30))


    
class UserLogin(BaseModel):
    email: str
    password: str
