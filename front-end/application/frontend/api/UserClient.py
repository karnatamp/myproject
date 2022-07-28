import requests
from flask import session, request


class UserClient:
    @staticmethod
    def post_login(form):
        api_key = False
        payload = {
            'username': form.username.data,
            'password': form.password.data
        }
        url = 'http://127.0.0.1:5002/api/user/login'
        response = requests.request("POST", url=url, data=payload)
        if response:
            d = response.json()
            if d['api_key'] is not None:
                api_key = d['api_key']
        return api_key

    @staticmethod
    def get_user():
        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        url = 'http://127.0.0.1:5002/api/user'
        response = requests.request(method="GET", url=url, headers=headers)
        user = response.json()
        return user

    @staticmethod
    def get_branches():
        url = "http://127.0.0.1:5002/api/getall-branch"
        response = requests.request(method="GET", url=url)
        branch = response.json()
        return branch.get('results')

    @staticmethod
    def get_roles():
        url = "http://127.0.0.1:5002/api/user-roles"
        response = requests.request(method="GET", url=url)
        roles = response.json()
        return roles.get('data')

    @staticmethod
    def post_user_reg(form):
        payload = {
            'first_name': form.firstname.data,
            'last_name': form.lastname.data,
            'email': form.email.data,
            'username': form.username.data,
            'password': form.password.data,
            'usertype': form.roles.data,
            'branch_id': form.branch.data,
            'address1': form.address1.data,
            'address2': form.address2.data,
            'address3': form.address3.data,
            'postal_code': form.postalcode.data,
            'city': form.city.data,
            'country': form.country.data
        }
        url = 'http://127.0.0.1:5002/api/user/create'
        response = requests.request("POST", url=url, data=payload)

        return response
        
    @staticmethod
    def post_branch_reg(form):
        pay_load = {
            'name': form.bname.data
        }
        url = 'http://127.0.0.1:5002/api/branch/create'
        response = requests.request('POST', url=url, data=pay_load)
        return response
        
    @staticmethod
    def roles(form):
        payload = {
            'name': form.rolename.data
        }
        url = 'http://127.0.0.1:5002/api/user-roles/create'
        response = requests.request("POST", url=url, data=payload)

        return response

    @staticmethod
    def get_all_users():
        url = "http://127.0.0.1:5002/api/users"
        response = requests.request(method="GET", url=url)
        users = response.json()
        return users

    @staticmethod
    def recommendation(form):
        payload = {
            'recommendation': form.recommendation.data
        }

        url = ' http://127.0.0.1:5002/api/student-recommendation/recommendation'
        response = requests.request("POST", url=url, data=payload)

        return response

    @staticmethod
    def feedback(form):
        payload = {
            'feedback': form.feedback.data
        }

        url = ' http://127.0.0.1:5002/api/student-recommendation/feedback'
        response = requests.request("POST", url=url, data=payload)

        return response