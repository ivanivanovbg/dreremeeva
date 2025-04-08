import datetime

from fastapi import FastAPI

app = FastAPI()

@app.get('/schedule/')
def get_schedule():
    month = datetime.datetime.now().month
    return "Schedule"