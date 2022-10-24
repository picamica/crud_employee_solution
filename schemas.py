from pydantic import BaseModel, EmailStr
from typing import Optional

class EmployeeSchema(BaseModel):
    name: str
    last_name: str
    hourly_rate: float
    coding_exp: int
    job_start_date: str


class CompanySchema(BaseModel):
    name: str

class SenioritySchemaBase(BaseModel):
    seniority: str
    time_to_reach: int


class SenioritySchema(SenioritySchemaBase):
    multiplier: float


class SenioritySchemaM(SenioritySchemaBase):
    multiplier: float = 0


class EmployeeUpdateSchema(BaseModel):
    email: Optional[EmailStr]
    hourly_rate: Optional[float]
    job_end_date: Optional[str]
    seniority: Optional[str]


class EmployeeOutBase(BaseModel):
    ID: int
    full_name: str
    email: str

    class Config:
        orm_mode = True


class EmployeeOutX(EmployeeOutBase):
    """
    Return model for (main.list_of_working_employees) function
    """
    annual_salary: float



class EmployeeOutZ(EmployeeOutBase):
    """
    Return model for (features.filter_before_date) function
    """
    seniority_level: str
    job_start_date: str
    is_still_working: bool
