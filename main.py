import random
from datetime import timedelta, datetime
from urllib.request import Request

import bcrypt
import jwt
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from fastapi.security.http import HTTPBase
from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.orm import Session
from starlette import status
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser, AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware

from db.Clas import EmailRequest, EmailRequest1
from db.connection import engine
from db.models import Base, Users, Email, Send_email, Send_emails

import smtplib
from email.mime.text import MIMEText

from fastapi import HTTPException
# 
app = FastAPI()
SECRET_KEY = "yoursecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

List = []


# class BearerTokenAuthBackend(AuthenticationBackend):
#
#     async def authenticate(self, request):
#         if "Authorization" not in request.headers:
#             return
#         if username := request.headers.get('Authorization'):
#             username = username.replace('Bearer ', '')
#             with Session(engine) as session:
#                 retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()
#                 if retrieved_user:
#                     return AuthCredentials(["authenticated"]), SimpleUser(username)
#
#         raise AuthenticationError({'detail': 'Invalid authorization'})

class BearerTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return
        if username := request.headers.get("Authorization"):
            username = username.replace('Bearer ', '')
            with Session(engine) as session:
                data = session.scalars(Select(Users)).all()
                for user in data:
                    if username == user.username:
                        return AuthCredentials(['authenticated']), SimpleUser(username)
        raise AuthenticationError({'detail': 'Invalid Authorization'})


app.add_middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend())
security = HTTPBase(scheme='bearer')

# app.add_middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend())
#
# security = HTTPBase(scheme='bearer')


# class User(BaseModel):
#     username: str
#     password: str
#
#
# class SignUp(User):
#     confirm_password: str
#
#     @classmethod
#     async def create(cls, username, password, confirm_password):
#         if password != confirm_password:
#             raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Invalid password provided')
#         with Session(engine) as session:
#             retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()
#             if retrieved_user:
#                 raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Username already in use')
#         salt = bcrypt.gensalt()
#         hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()
#         return User(username=username, password=hash)
#
#
# class SignIn(User):
#     @classmethod
#     async def check(cls, username, password):
#         with Session(engine) as session:
#             retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()
#             if retrieved_user:
#                 result = bcrypt.checkpw(password.encode('utf-8'), retrieved_user['password'].encode('utf-8'))
#                 if not result:
#                     return {'message': 'Successfully signed with %s' % username}
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Invalid username/password provided')


@app.post('/signup')
async def create(username, email):
    with Session(engine) as session:
        data = session.scalars(Select(Users)).all()
        for user in data:
            users = user.username
            if username == users:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Username already in use')
    salt = bcrypt.gensalt()
    s: Users = Users(username=username, email=email)
    session.add(s)
    session.commit()
    return {'message': 'Sign Up Successfully'}

#
# @app.get('/profile', dependencies=[Depends(security)])
async def profile(request: Request):
    if request.user.is_authenticated:
        return Users(username=request.username, email=request.user.email)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)




@app.get("/")
async def root():
    with Session(engine) as session:
        Name = session.scalars(Select(Users)).all()
    return Name


@app.post("/username")
async def append(username: str = Form(...), email: str = Form(...), ):
    name: Users = Users(username=username, email=email)
    with Session(engine) as session:
        session.add(name)
        session.commit()
        Name = session.scalars(Select(Users)).all()
    users = session.execute(
        select(Users).where((Users.username == username))
    ).all()
    return Name


def create_jwt_token(data):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/login")
async def say_hello(username: str):
    with Session(engine) as session:
        retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()

        if retrieved_user:
            access_token = create_jwt_token(data={"sub": username})
            return {"message": "muvaffaqiyatli o'tildi ", "user": retrieved_user,
                    'access_token': access_token}
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "username yoq")


@app.get("/Emaillar")
async def emaillar():
    with Session(engine) as session:
        name = session.scalars(Select(Users.email)).all()
        # Name = session.scalars(Select(Users)).all()
    return (name)


@app.post("/Emaillar")
async def emaillar(username: str):
    with Session(engine) as session:
        retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()
        if retrieved_user:
            name = session.scalars(Select(Users.email)).all()
            emails = session.execute(select(Users.email).where(Users.username == username)).scalars().all()
            return emails
    raise HTTPException(status.HTTP_404_NOT_FOUND, "topilmadi")







# email in user account ForeignKey

@app.post("/emails/in_user_foreignkey")
async def append(email: str = Form(...), user_id: int = Form(...)):
    new_email = Email(email=email, user_id=user_id)

    with Session(engine) as session:
        try:
            added_email = session.query(Email).filter_by(email=email, user_id=user_id).first()
            if not added_email:
                session.add(new_email)
                session.commit()
                return new_email
        except Exception as e:
            return f"An error occurred: {e}"




from starlette import status


def sen_email(username: str, subject: str, body: str):

    with Session(engine) as session:
        retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()
        if retrieved_user:
            to_email = session.execute(select(Users.email).where(Users.username == username)).scalars().all()

            sender_email = "boronovshahriyor2004@gmail.com"
            sender_password = "sqip huze ceri llpz"

            message = MIMEText(body)
            message["Subject"] = subject
            message["From"] = sender_email

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, to_email, message.as_string())
                return f"Email sent to {to_email} successfully!"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")
    raise HTTPException(status.HTTP_404_NOT_FOUND, "user yo'q")


@app.post("/username in email/")
async def send_email_endpoint(email_request: EmailRequest1):
    sen_email(email_request.username, email_request.subject, email_request.body)

    return {"message": "yuborildi !"}



# import smtplib
# import random
# from email.mime.text import MIMEText
# from fastapi import FastAPI, HTTPException
# from sqlalchemy import select
# from sqlalchemy.orm import Session
#
# from db.Clas import EmailRequest, EmailRequest1
# from db.connection import engine
# from db.models import Users, Send_email
#
# # from Clas import EmailRequest, Users, Send_email, engine  # Update with your actual imports
#
# app = FastAPI()


#
# def send_email_with_code(username: str, to_email: str):
#     random_code = generate_random_code()
#     body = f"Tasdiqlash kodingiz: {random_code}"
#
#     name = Send_email(username=username, to_email=to_email, subject="Tasdiqlash kodingiz", body=body)
#
#     with Session(engine) as session:
#         retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()
#         if retrieved_user:
#             sender_email = "boronovshahriyor2004@gmail.com"
#             sender_password = "sqip huze ceri llpz"
#
#             message = MIMEText(body)
#             message["Subject"] = "Tasdiqlash kodingiz"
#             message["From"] = sender_email
#             message["To"] = to_email
#
#             try:
#                 with smtplib.SMTP("smtp.gmail.com", 587) as server:
#                     server.starttls()
#                     server.login(sender_email, sender_password)
#                     server.sendmail(sender_email, to_email, message.as_string())
#                     session.add(name)
#                     session.commit()
#                 return random_code
#             except Exception as e:
#                 raise HTTPException(status_code=500, detail=f"xatolik yuz berdi: {str(e)}")
#         else:
#             raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
#
#
# @app.post("/send-verification-code/")
# async def send_verification_code(email_request: EmailRequest):
#     try:
#         verification_code = send_email_with_code(email_request.username, email_request.to_email)
#         return {"message": f"Tasdiqlash kodi yuborildi {email_request.to_email} successfully.", "code": verification_code}
#     except HTTPException as e:
#         return e

# nourimanov@gmail.com


def send_email():
    pass
def generate_random_code():
    return str(random.randint(100000, 999999))

def send_email(username: str, to_email: str, subject: str, body: str):
    random_code = generate_random_code()
    body = f"Tasdiqlash kodingiz: {random_code}"

    # name = Send_email(username=username, to_email=to_email, subject="Tasdiqlash kodingiz", body=body)
    name: Send_email = Send_email(username=username, to_email=to_email, subject=subject, body=body)

    with Session(engine) as session:
        retrieved_user = session.execute(select(Users).where(Users.username == username)).scalar()
        if retrieved_user:
            sender_email = "boronovshahriyor2004@gmail.com"
            sender_password = "sqip huze ceri llpz"

            message = MIMEText(body)
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = to_email

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, to_email, message.as_string())
                    session.add(name)
                    session.commit()
                return f"Email sent to {to_email} successfully!"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")
    raise HTTPException(status.HTTP_404_NOT_FOUND, "user yo'q")


@app.post("/1-email/")
async def send_email_endpoint(email_request: EmailRequest):
    send_email(email_request.username, email_request.to_email, email_request.subject, email_request.body)

    return {"message": "yuborildi !"}



