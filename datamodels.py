import datetime
from typing import Any

from pydantic import BaseModel

days_of_week = ("Понеделник", "Вторник", "Сряда", "Четвъртък", "Петък", "Събота", "Неделя")

class WorkDay(BaseModel):
    id:int
    wday_from:datetime.datetime
    wday_to:datetime.datetime
    string_representation:str|None=None

    def model_post_init(self, context: Any, /) -> None:
        self.string_representation = f"""{
        str(self.wday_from.day).zfill(2)}.{
        str(self.wday_from.month).zfill(2)}.{
        self.wday_from.year}г. ({
        days_of_week[self.wday_from.weekday()]}) от {
        str(self.wday_from.hour).zfill(2)}:{
        str(self.wday_from.minute).zfill(2)} до {
        str(self.wday_to.hour).zfill(2)}:{
        str(self.wday_to.minute).zfill(2)}"""

class Schedule(BaseModel):
    workdays:list[WorkDay]|list

