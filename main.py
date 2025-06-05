import datetime
import sqlite3
from typing import Annotated
from fastapi import FastAPI,Form
from datamodels import Schedule,WorkDay
from datetime import datetime,timedelta,timezone
import jwt
from fastapi.middleware.cors import CORSMiddleware
from hashlib import sha256
from pydantic import BaseModel
import uvicorn

app = FastAPI()
TOKEN_KEY = "81c9121387b311bb5b4b31f4da9646f0c119f2b5c1fd2c53d244b60ec3715133"
TOKEN_ALG = "HS256"

origins = [
    "http://www.dr-eremeeva.com",
    "https://www.dr-eremeeva.com",
    "http://dr-eremeeva.com",
    "https://dr-eremeeva.com"
    # or "*" to allow all origins (less secure)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Token(BaseModel):
    token:str

class TokenResponse(BaseModel):
    result:bool

def get_db_conn()->sqlite3.Connection:
    return sqlite3.connect("eremeeva.db")

@app.get('/schedule/')
def get_schedule():
    dbconn = get_db_conn()
    dbcursor = dbconn.cursor()
    month = datetime.now().month
    year = datetime.now().year
    month_query = "SELECT id,datetime(`from`),datetime(`to`) FROM workdays WHERE `month`=? AND `year`=?"
    query_args = (month,year)
    month_res = dbcursor.execute(month_query,query_args)
    month_schedule = Schedule(workdays=[])
    for res_item in month_res.fetchall():
        month_schedule.workdays.append(WorkDay(id=res_item[0],wday_from=res_item[1],wday_to=res_item[2]))
    dbconn.close()
    return month_schedule

@app.get('/schedule/month/{month}/year/{year}/')
def get_schedule_month(month:int,year:int):
    dbconn = get_db_conn()
    dbcursor = dbconn.cursor()
    month_query = "SELECT id,datetime(`from`),datetime(`to`) FROM workdays WHERE `month`=? AND `year`=?"
    query_args = (month,year)
    month_res = dbcursor.execute(month_query,query_args)
    month_schedule = Schedule(workdays=[])
    for res_item in month_res.fetchall():
        month_schedule.workdays.append(WorkDay(id=res_item[0],wday_from=res_item[1],wday_to=res_item[2]))
    dbconn.close()
    return month_schedule

@app.post('/schedule/')
def enter_schedule_month(day:Annotated[str,Form()],month:Annotated[str,Form()],year:Annotated[str,Form()],hfrom:Annotated[str,Form()],mfrom:Annotated[str,Form()],hto:Annotated[str,Form()],mto:Annotated[str,Form()],token:Annotated[str,Form()]):
    if check_token(token):
        dbconn = get_db_conn()
        dbcursor = dbconn.cursor()
        wday_from = datetime(year=int(year),month=int(month),day=int(day),hour=int(hfrom),minute=int(mfrom))
        wday_to = datetime(year=int(year),month=int(month),day=int(day),hour=int(hto),minute=int(mto))
        month_query = "INSERT INTO workdays(`from`,`to`,`year`,`month`,`day`) VALUES(datetime(?),datetime(?),?,?,strftime('%d',?))"
        query_args = (wday_from,wday_to,year,month,wday_from)
        dbcursor.execute(month_query,query_args)
        dbconn.commit()
        dbconn.close()
        return True
    else:
        return False

@app.post('/login/')
def perform_login(username:Annotated[str,Form()],password:Annotated[str,Form()])->Token|bool:
    correct_username = "Anna"
    correct_password = "722e07c6f08abc06c5ddd3d9254652fdbbadf1e1acc8d30482cd8fda1c553cde"
    if sha256(password.encode('utf-8')).hexdigest() == correct_password and username == correct_username:
        payload = {
            "sub":username,
            "exp":(datetime.now(timezone.utc) + timedelta(days=10))
        }
        return Token(token=jwt.encode(payload=payload,algorithm=TOKEN_ALG,key=TOKEN_KEY))
    else:
        return False

@app.post('/token/check/')
def check_token(token:Annotated[str,Form()])->TokenResponse:
    try:
        payload = jwt.decode(jwt=token,algorithms=[TOKEN_ALG],key=TOKEN_KEY)
        if payload:
            return TokenResponse(result=True)
    except (jwt.exceptions.ExpiredSignatureError,jwt.exceptions.InvalidSignatureError,jwt.exceptions.DecodeError) as e:
            return TokenResponse(result=False)

@app.post('/schedule/delete/')
def update_schedule_month(wd_id:Annotated[str,Form()],token:Annotated[str,Form()]):
    if check_token(token):
        dbconn = get_db_conn()
        dbcursor = dbconn.cursor()
        wd_id = int(wd_id)
        delete_query = "DELETE FROM workdays WHERE `id`=?"
        query_args = (wd_id,)
        dbcursor.execute(delete_query,query_args)
        dbconn.commit()
        dbconn.close()
        return True
    return False

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)