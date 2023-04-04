from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.fields import DatetimeField, TextField
from tortoise.models import Model


class TextSummary(Model):
    url = TextField()
    summary = TextField()
    created_at = DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.url


SummarySchema = pydantic_model_creator(TextSummary)


class BaseModel(Model):
    model_name: str
    model_age: int
