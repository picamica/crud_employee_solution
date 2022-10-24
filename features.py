import datetime
from dbmodels import Company, Employee, SeniorityLevel, load_session, EmployeeConfigured
from sqlalchemy.sql import exists
from sqlalchemy import desc





session = load_session()


def company_by_id(company_id: int) -> object:
    return session.query(Company).filter_by(ID = company_id).first()


def multiply_hourly(company_id: int, seniority: str, hourly_rate: float) -> float:
    """
    Function that returns multiplied hourly rate against seniority multiplier number
    """
    query = session.query(SeniorityLevel).filter(SeniorityLevel.company_id == company_id,
                                                 SeniorityLevel.seniority == seniority).first()
    return query.multiplier * hourly_rate


def add_company(company_name: str) -> int:
    """
    Function that creates company record in the database
    also assigns default seniority levels (see default_seniority function)
    """
    company = Company(company_name)
    default_seniority(company)
    return company.ID


def insert_employees(company_id: int, employees: list):
    """
    A function that takes clients list of employees
    and creates records in the database according

    Seniority level is assigned automatically with function *assign_seniority*
    Hourly rate is set by *multiply_hourly* function
    """
    company = company_by_id(company_id)
    name = company.company_name

    for employee in employees:
        job_start_date = datetime.datetime.strptime(employee.job_start_date, '%Y-%m-%d').date()
        email = set_email(employee.name, employee.last_name, name)
        seniority_level = assign_seniority(employee.coding_exp, job_start_date, company_id)
        hourly = multiply_hourly(company_id, seniority_level, employee.hourly_rate)

        company.employee_children.append(Employee(employee.name,
                                                  employee.last_name,
                                                  email,
                                                  seniority_level,
                                                  hourly,
                                                  job_start_date))
        session.commit()


def insert_seniority_level(company_id: int, seniority: dict):
    """
    Function that creates a new seniority level record in database
    """
    company = company_by_id(company_id)
    seniority_obj = SeniorityLevel(seniority['seniority'].lower(),
                                   seniority['time_to_reach'],
                                   seniority['multiplier'])

    company.seniority_children.append(seniority_obj)
    session.commit()


def update_seniority_reach(company_id: int, seniority_schema: dict):
    """
    Function that updates companies seniority level reach time

    if multiplier is also passed by endpoint user, then it is
    updated in database accordingly
    """
    seniority_level = session.query(SeniorityLevel).filter(
                                                          SeniorityLevel.seniority == seniority_schema['seniority'].lower(),
                                                          SeniorityLevel.company_id == company_id)
    if seniority_schema['multiplier'] != 0:
        seniority_level.update({'multiplier': seniority_schema['multiplier'],
                               'time_to_reach': seniority_schema['time_to_reach']})
    else:
        seniority_level.update({'time_to_reach': seniority_schema['time_to_reach']})

    session.commit()

def default_seniority(company: Company):
    """
    Function that appends default seniority levels
    to each company created in the database
    """
    seniority = [SeniorityLevel('junior', 0, 1.0),
                 SeniorityLevel('mid', 2, 1.25),
                 SeniorityLevel('senior', 5, 1.75)]

    for i in seniority:
        company.seniority_children.append(i)

    session.add(company)
    session.commit()


def set_email(first_name: str, last_name: str, company_name: str) -> str:
    """
    Function that generates employee company email

    In case email already exists, we add a number at the end
    """
    mail = '{0}.{1}@{2}.com'.format(first_name, last_name, company_name).lower()

    #True or False
    email_exists = session.query(exists().where(Employee.email==mail)).scalar()

    if email_exists:
        query = session.query(Employee).filter_by(first_name=first_name, last_name=last_name)
        num = 0
        for i in query:
            num += 1
        mail = mail.split('@')[0] + str(num) + '@' + mail.split('@')[1]
    return mail


def assign_seniority(exp_before_company: int, job_start_date: datetime.date,
                     company_id: int) -> str:
    """
    Function that assigns employee seniority level according to
    his/her work experience before company + in the company
    """
    since_job_start = datetime.datetime.now().year - job_start_date.year
    total_exp = exp_before_company + since_job_start
    seniority = ''
    print(total_exp)

    seniority_levels = session.query(SeniorityLevel).filter_by(company_id = company_id).order_by(desc(SeniorityLevel.time_to_reach)).all()

    for level in seniority_levels:
        if total_exp >= level.time_to_reach:
            return level.seniority


def filter_before_given_date(company_id: int, given_date: str) -> list:
    """
    Function that filters out company employees
    up to the date that was passed in (given_date)
    and returns a list of them if they are still working
    """
    stripped_date = datetime.datetime.strptime(given_date, '%Y-%m-%d')

    queries = session.query(Employee).filter(Employee.company_id == company_id,
                                             Employee.job_start_date <= stripped_date).all()

    json_list = []

    for query in queries:
        is_currently_working = 'No' if query.job_end_date is not None else 'Yes'
        json_list.append(EmployeeConfigured(
                                            query.company_id,
                                            '{0} {1}'.format(query.first_name, query.last_name),
                                            query.email,
                                            seniority=query.seniority_level,
                                            job_start_date=datetime.datetime.strftime(query.job_start_date, '%Y-%m-%d'),
                                            is_still_working=is_currently_working))
    return json_list


def get_list_of_working_employees(company_id: int) -> list:
    """
    Function that returns a list of currently working employees objects
    """
    annual_hours = (40 * 4) * 12
    queries =session.query(Employee).filter(
                                          Employee.company_id == company_id,
                                          Employee.job_end_date == None
                                          ).all()
    configured_employees = []
    for i in queries:
        configured_employees.append(EmployeeConfigured(i.ID, '{0} {1}'.format(i.first_name,
                                                        i.last_name),i.email,
                                                        annual_salary=i.hourly_rate * annual_hours))

    return configured_employees


def get_employee_by_id(employee_id: int) -> object:
    return session.query(Employee).filter_by(ID = employee_id)


def update_employee_email(email: str, employee_id: int):

    employee = get_employee_by_id(employee_id)
    employee.update({'email': email})
    session.commit()


def update_employee_seniority(employee_id: int, company_id: int, seniority: str):

    seniority_levels = [i.seniority for i in session.query(SeniorityLevel).filter_by(
                                                                                     company_id = company_id)]
    employee = get_employee_by_id(employee_id)
    if seniority.lower() not in seniority_levels:
        return 'Seniority level does not exist'
    else:
        updated_hourly_rate = multiply_hourly(company_id, seniority.lower(),
                                              employee[0].hourly_rate)
        employee.update({'seniority_level': seniority.lower(),
                        'hourly_rate': round(updated_hourly_rate, 1)})
        session.commit()


def update_employee_hourly_rate(company_id: int, employee_id: int, hourly_rate: float):

    employee = get_employee_by_id(employee_id)
    seniority_level = session.query(SeniorityLevel).filter_by(company_id = company_id,
                                                    seniority = employee[0].seniority_level).first()
    employee.update({'hourly_rate': round(hourly_rate * seniority_level.multiplier)})
    session.commit()


def update_employee_job_end_date(employee_id: int, job_end_date: str):
    employee = get_employee_by_id(employee_id)
    job_end_date = datetime.datetime.strptime(job_end_date, '%Y-%m-%d')
    employee.update({'job_end_date': job_end_date})
    session.commit()
