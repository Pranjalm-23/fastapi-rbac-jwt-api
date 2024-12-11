from typing import Literal
from pydantic import BaseModel

# Models
class UserModel(BaseModel):
    username: str
    password: str
    role: Literal["user", "admin"]

class ProjectModel(BaseModel):
    name: str
    description: str

class ProjectOutModel(BaseModel):
    id: str
    name: str
    description: str