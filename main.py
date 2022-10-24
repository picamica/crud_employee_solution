import datetime

from fastapi import FastAPI

from typing import List

from schemas import EmployeeSchema, CompanySchema, SenioritySchema, SenioritySchemaM, EmployeeUpdateSchema, EmployeeOutX, EmployeeOutZ

from features import filter_before_given_date, get_list_of_working_employees, add_company, insert_employees, insert_seniority_level, update_seniority_reach, update_employee_email, update_employee_seniority, update_employee_hourly_rate, update_employee_job_end_date

from dbmodels import load_session, Employee, create_db




create_db()
session = load_session()
app = FastAPI()


@app.get('/employee/list/{company_id}/', response_model=List[EmployeeOutX])
def return_working_employees(company_id: int):
    return [EmployeeOutX.from_orm(i) for i in get_list_of_working_employees(company_id)]


@app.get('/beforedate/{company_id}/', response_model=List[EmployeeOutZ])
def before_date(company_id: int, date: str = datetime.datetime.today().strftime("%Y-%m-%d")):
    print(date)
    return [EmployeeOutZ.from_orm(i) for i in filter_before_given_date(company_id, date)]


@app.post('/add/company/')
def insert_company(company: CompanySchema):
    return 'ID for future use of API: {0}'.format(add_company(company.name))


@app.post('/add/employee/{company_id}/')
def add_employees(employees: List[EmployeeSchema], company_id: int):
    insert_employees(company_id, employees)


@app.post('/add/seniority/{company_id}/')
def add_seniority(company_id: int, seniority: SenioritySchema):
    insert_seniority_level(company_id, seniority.dict())


@app.put('/update/seniorityreach/{company_id}')
def update_sen_reach(company_id: int, reach_schema: SenioritySchemaM):
    update_seniority_reach(company_id, reach_schema.dict())


@app.put('/update/employee/{company_id}/{employee_id}/')
def update_employee(company_id: int, employee_id: int, data: EmployeeUpdateSchema):

    if data.email is not None:
        update_employee_email(data.email, employee_id)

    if data.seniority is not None:
        return update_employee_seniority(employee_id, company_id, data.seniority)

    if data.hourly_rate is not None:
        update_employee_hourly_rate(company_id, employee_id, data.hourly_rate)

    if data.job_end_date is not None:
        update_employee_job_end_date(employee_id, data.job_end_date)



@app.delete('/delete/employee/{company_id}/{employee_id}/')
def delete_employee(company_id: int, employee_id: int):

    try:
        session.query(Employee).filter_by(company_id = company_id, ID = employee_id).delete()
        session.commit()
        return 'Successfully deleted'
    except Exception as e:
        return e

