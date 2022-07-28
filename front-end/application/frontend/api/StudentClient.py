import requests
from flask import session, request

class StaffClient:

    @staticmethod
    def student_reg(form):
        # " //studentname rollnumber email username password gender dob parentname  pemail address1 address2 address3 postalcode city country"
        payload = {
            'studentname': form.studentname.data,
            'firstname': form.rollnumber.data,
            'lastname': form.email.data,
            'username': form.username.data,
            'password': form.password.data,
            'gender': form.gender.data,
            'department': form.dob.data,
            'branch': form.parentname.data,
            'branch': form.pemail.data,
            'address1': form.address1.data,
            'address2': form.address2.data,
            'address3': form.address3.data,
            'postalcode': form.postalcode.data,
            'city': form.city.data,
            'country': form.country.data,
            'country': form.phone.data,
        }
        url = ' http://127.0.0.1:5002/api/department/create'
        response = requests.request("POST", url=url, data=payload)
        return response