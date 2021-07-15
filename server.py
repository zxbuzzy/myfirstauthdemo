import hashlib
import hmac
import base64

from typing import Optional
from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response

# Создание экземпляра приложения
app = FastAPI()


#Сгенерировано в openssl
SECRET_KEY = 'd485c8826e9aaf9a025957ba0a71347736891c8a319e5bcc6b0d0f85384d68df'
PASSWORD_SALT = '9a616eb54605e906551accca1102af272e9bea1ac6ac2caaaba1b1c47085a378'

users = {
    'nikita@user.com': {
        'name': 'Никита',
        'password': '16a5e732974911b9ba427d02a344f3d3627aecae25edefce18b048b83ad5c76b',
        'balance': 100_000
    },
    'alice@user.com': {
        'name': 'Алиса',
        'password': 'd0c4daaea67fa83d80a862e1134c3b674d46767bb998fe2f19bcb368afb6dd07',
        'balance': 500_000
    }
}


# Подпись данных
def sign_data(data: str) -> str:
    """Возвращает подписанные данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()
    

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
    return password_hash == stored_password_hash

# Декоратор для указания адреса и типа запроса на который нужно вызвать функцию
@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type='text/html')
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key='username')
        return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key='username')
        return response
    return Response(f'Привет, {users[valid_username]["name"]}!', media_type='text/html')



@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    print(user, password)
    if not user or not verify_password(username, password):
        return Response("Я вас не знаю", media_type='text/html')
    
    response = Response(
        f"Привет, {user['name']}!<br />Баланс: {user['balance']}",
        media_type='text/html')
    username_signed = base64.b64encode(username.encode()).decode() + "." + sign_data(username)
    response.set_cookie(key='username', value=username_signed)
    
    return response
    


