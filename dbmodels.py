import os
import datetime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Date, create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import exists
from sqlalchemy_utils import EmailType
from typing import Optional






ENGINE = create_engine('sqlite:///project.db', connect_args={'check_same_thread': False})
BASE = declarative_base(ENGINE)

def load_session():
    metadata = BASE.metadata
    Session = sessionmaker(bind = ENGINE)
    session = Session()
    return session


def create_db():
  if os.path.isfile('project.db'):
    pass
  else:
    BASE.metadata.create_all()


class Company(BASE):
    __tablename__ = 'Company'

    ID = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    seniority_children = relationship('SeniorityLevel', back_populates='company_parent')
    employee_children = relationship(
                                  'Employee',
                                  back_populates='company_parent',
                                  cascade='all, delete')

    def __init__(self, company_name: str):
        self.company_name = company_name


class SeniorityLevel(BASE):
    __tablename__ = 'SeniorityLevel'

    ID = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('Company.ID'))
    seniority = Column(String, nullable=False)
    time_to_reach = Column(Integer, nullable=False)
    multiplier = Column(Float, nullable=False)
    company_parent = relationship('Company', back_populates='seniority_children')


    def __init__(self, seniority: str, time_to_reach: int, multiplier: float):
        self.seniority = seniority
        self.time_to_reach = time_to_reach
        self.multiplier = multiplier


class Employee(BASE):
    __tablename__ = 'Employee'

    ID = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('Company.ID'), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(EmailType, nullable=False)
    seniority_level = Column(String, nullable=False)
    hourly_rate = Column(Float, nullable=False)
    job_start_date = Column(DateTime, nullable=False)
    job_end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    company_parent = relationship('Company', back_populates='employee_children')


    def __init__(self, first_name: str, last_name: str, email: str,
                 seniority_level: str, hourly_rate: float, job_start_date: datetime.date):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.seniority_level = seniority_level
        self.hourly_rate = hourly_rate
        self.job_start_date = job_start_date


class EmployeeConfigured:
    """
    Class used to create objects for pydantic models
    to return in api call
    """
    def __init__(self, ID: int, full_name: str, email: str, annual_salary=None,
                 job_start_date=None, is_still_working=None, seniority=None):
        self.ID = ID
        self.full_name = full_name
        self.email = email
        self.annual_salary = annual_salary
        self.job_start_date = job_start_date
        self.is_still_working = is_still_working
        self.seniority_level = seniority
