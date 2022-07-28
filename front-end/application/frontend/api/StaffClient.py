import requests
from flask import session, request

class StaffClient:

    @staticmethod
    def department_reg(form):
        payload = {
            'name': form.dname.data
        }
        url = ' http://127.0.0.1:5002/api/department/create'
        response = requests.request("POST", url=url, data=payload)
        return response

    @staticmethod
    def get_departments():
        url = "http://127.0.0.1:5002/api/department"
        response = requests.request(method="GET", url=url)
        branch = response.json()
        return branch

    @staticmethod
    def get_staff_latest_code():
        url = "http://127.0.0.1:5002/api/gen-staff-code"
        response = requests.request(method="GET", url=url)
        branch = response.json()
        return branch

    @staticmethod
    def post_staff_reg(form):
        payload = {
            'staffcode': form.staffcode.data,
            'firstname': form.firstname.data,
            'lastname': form.lastname.data,
            'username': form.username.data,
            'password': form.password.data,
            'gender': form.gender.data,
            'department': form.department.data,
            'branch': form.branch.data,
            'address1': form.address1.data,
            'address2': form.address2.data,
            'address3': form.address3.data,
            'postalcode': form.postalcode.data,
            'city': form.city.data,
            'country': form.country.data,
            'date_of_birth': form.dob.data,
            'email': form.email.data,
            'mobile': form.phone.data,
        }
        url = 'http://127.0.0.1:5002/api/staff/create'
        response = requests.request("POST", url=url, data=payload)

        return response