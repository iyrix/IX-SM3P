from pydantic import BaseModel


class Task(BaseModel):
    task_id: str
    task_name: str
    description: str
    column_id: str
    index: str



