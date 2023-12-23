from pydantic import BaseModel

class ToDoBody(BaseModel):
    email_message: str
    # sender: str
    # subject: str
    # date: str

class ToDoResponse(BaseModel):
    next_step: str
    action: str
    deadline: str
    summary: str
    effort: str
    constraint: str