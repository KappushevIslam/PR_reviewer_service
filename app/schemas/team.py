from pydantic import BaseModel


class TeamMember(BaseModel):
    user_id: str
    username: str
    is_active: bool
    
    class Config:
        from_attributes = True


class Team(BaseModel):
    team_name: str
    members: list[TeamMember]
    
    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    team_name: str
    members: list[TeamMember]

