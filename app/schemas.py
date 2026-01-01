from pydantic import BaseModel


#fields required to accept a post
class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    title: str
    content: str
