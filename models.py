from pydantic import BaseModel

class RequestData(BaseModel):
    tweet_id: str

class Task(BaseModel):
    # Celery task representation
    task_id: str
    status: str


class Result(BaseModel):
    # Celery task result
    task_id: str
    status: str