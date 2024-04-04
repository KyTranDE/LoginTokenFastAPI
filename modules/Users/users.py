from typing import Union
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: Union[str, None] = None
    password: str
    phone_number : Union[str, None] = None
    
class UserLogin(BaseModel):
    email: str
    password: str

