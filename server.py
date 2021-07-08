from fastapi import FastAPI, Form
from fastapi.responses import Response

# Создание экземпляра приложения
app = FastAPI()

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


# Декоратор для указания адреса и типа запроса на который нужно вызвать функцию
@app.get('/')
def index_page():
    with open('templates/login.html') as f:
        login_page = f.read()
    return Response(login_page, media_type="text/html")


@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    try:
        user = users[username]
        if user['password'] != password:
            return Response('Неверный логин', media_type='text/html')
        else:
            return Response(
                f'Привет, {user["name"]}<br />Баланс: {user["balance"]}',
                media_type='text/html'
            )
    except KeyError:
        return Response("Я вас не знаю:(", media_type='text/html')
