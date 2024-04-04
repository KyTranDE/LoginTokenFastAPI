import re
from fastapi import HTTPException, status

class Check():
    def __init__(self):
        pass
    def is_valid_email(self, user):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email không hợp lệ")
    def is_valid_password(self, user):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu phải chứa ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt")
    def is_valid_phone_number(self, user):
        if not re.match(r'^(\+\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$', user.phone_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Số điện thoại không hợp lệ")


    