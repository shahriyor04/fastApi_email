from pydantic import BaseModel


class Username(BaseModel):
    username: str
    email: str


class EmailRequest(BaseModel):
    username: str
    to_email: str
    subject: str
    body: str


class EmailRequest1(BaseModel):
    username: str
    subject: str
    body: str