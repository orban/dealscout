from typing import Dict

from peewee import (
    Model,
    CharField,
    AutoField,
    BooleanField)
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

db = SqliteExtDatabase('requests.db')


class BaseModel(Model):
    class Meta:
        database = db


class Request(BaseModel):
    id = AutoField()
    text = CharField()
    media = CharField()
    started = BooleanField(default=False)


def get_latest_request() -> Request or None:
    try:
        return Request.select().order_by(Request.id.desc()).get()
    except Request.DoesNotExist:
        return None


def create_new_request(text: str, media: Dict = {}, started: bool = False):
    Request.create(text=text, media=media, started=started)


def update_request_by_id(request_id: int, text: str, media: Dict, started: bool):
    query = Request.update({Request.text: text,
                           Request.media: media,
                           Request.started: started}).where(Request.id == request_id)
    updated = query.execute()
    return updated > 0


db.connect()
db.create_tables([Request], safe=True)
