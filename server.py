import hashlib
import hmac
from typing import Optional
from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response

# Создание экземпляра приложения
app = FastAPI()

SECRET_KEY = 'd485c8826e9aaf9a025957ba0a71347736891c8a319e5bcc6b0d0f85384d68df'

users = {
    'nikita@user.com': {
        'name': 'Никита',
        'password': 'password1',
        'balance': 100_000
    },
    'alice@user.com': {
        'name': 'Алиса',
        'password': 'password2',
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


# Декоратор для указания адреса и типа запроса на который нужно вызвать функцию
@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html') as f:
        login_page = f.read()
    # if username:
    #     try:
    #         user = users[username]
    #     except KeyError:
    #         response = Response(login_page, media_type='text/html')
    #         response.delete_cookie(key='username')
    #         return response
    if user := users.get(username):
        return Response(f'Привет, {users[username]["name"]}', media_type='text/html')
    else:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key='username')
        return response



@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    try:
        user = users[username]
        if user['password'] != password:
            return Response('Неверный логин', media_type='text/html')
        else:
            response = Response(
                f'Привет, {user["name"]}<br />Баланс: {user["balance"]}',
                media_type='text/html'
            )
            response.set_cookie(key='username', value=username)
            return response
    except KeyError:
        return Response("Я вас не знаю:(", media_type='text/html')
