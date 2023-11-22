from pydantic import BaseModel
from typing import List
from models.task_model import Task


class Column(BaseModel):
    column_id: str
    tasks: List[Task]





