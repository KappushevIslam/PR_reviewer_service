from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    username: str
    team_name: str
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    user_id: str
    is_active: bool
