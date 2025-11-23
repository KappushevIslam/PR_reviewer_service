from enum import Enum

from pydantic import BaseModel


class ErrorCode(str, Enum):
    TEAM_EXISTS = "TEAM_EXISTS"
    PR_EXISTS = "PR_EXISTS"
    PR_MERGED = "PR_MERGED"
    NOT_ASSIGNED = "NOT_ASSIGNED"
    NO_CANDIDATE = "NO_CANDIDATE"
    NOT_FOUND = "NOT_FOUND"


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
