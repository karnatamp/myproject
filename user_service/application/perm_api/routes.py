from . import perm_api_blueprint
from .. import db, login_manager
from ..models import Roles, User, Pageallocation, Userpriviledge, Branch, Useraddress, Staffstructure, Staff, \
    Studentregistration, Studentattendance, Studentfee, Paper_creation, Questions, Answers, Examresults, Exambooking, \
    Course, Subjects, Recommendation ,Feedback,MultinomialNB,NLP
from flask import make_response, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from passlib.hash import sha256_crypt
from collections import defaultdict
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import nltk
import ssl
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB

"""
use to reload the user object from the userid stored in session
"""


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


"""
sometime we have to login users without using cookies
such as using header values
or an API key args as a query argument, in this cases we have to use
request_loader
"""


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    return None


@perm_api_blueprint.route('/api/users', methods=['GET'])
def get_users():
    data = []
    for row in User.query.all():
        data.append(row.to_json())
    response = jsonify(data)
    return response


def set_privilege(userid):
    pages = Pageallocation.query.all()

    for row in pages:
        item = Userpriviledge()
        json_data = row.to_json()
        page_id = json_data.get('id')

        item.user_id = userid
        item.pageallocation_id = page_id
        db.session.add(item)
        db.session.commit()


# No returns since this method is called within a function


@perm_api_blueprint.route('/api/user/create', methods=['POST'])
def user_register():
    # Address Form
    address1 = request.form['address1']
    address2 = request.form['address2']
    address3 = request.form['address3']
    city = request.form['city']
    country = request.form['country']
    postal_code = request.form['postal_code']
    item_add = Useraddress()
    item_add.address1 = address1
    item_add.address2 = address2
    item_add.address3 = address3
    item_add.city = city
    item_add.country = country
    item_add.postal_code = postal_code
    db.session.add(item_add)
    db.session.commit()

    result = item_add.to_json()
    insert_addr_id = result.get('id')

    # USER FORM

    username = request.form['username']
    email = request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    usertype = request.form['usertype']
    branch_id = request.form['branch_id']

    password = sha256_crypt.hash((str(request.form['password'])))

    user = User()
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.password = password
    user.username = username
    user.authenticated = True
    user.role_id = usertype
    user.address_id = insert_addr_id
    user.branch_id = branch_id

    db.session.add(user)
    db.session.commit()
    result = user.to_json()

    response = jsonify({'message': 'User added', 'result': result})

    # When User is created, Priviledges are set
    set_privilege(result.get('id'))
    return response


@perm_api_blueprint.route('/api/user/login', methods=['POST'])
def post_login():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user:
        if sha256_crypt.verify(str(request.form['password']), user.password):
            user.encode_api_key()
            db.session.commit()
            login_user(user)

            return make_response(jsonify({'message': 'Logged in', 'api_key': user.api_key}))

    return make_response(jsonify({'message': 'Not logged in'}), 401)


@perm_api_blueprint.route('/api/user/logout', methods=['POST'])
def post_logout():
    if current_user.is_authenticated:
        logout_user()
        return make_response(jsonify({'message': 'You are logged out'}))
    return make_response(jsonify({'message': 'You are not logged in'}))


@perm_api_blueprint.route('/api/user/<username>/exists', methods=['GET'])
def get_username(username):
    item = User.query.filter_by(username=username).first()
    if item is not None:
        response = jsonify({'result': True})
    else:
        response = jsonify({'message': 'Cannot find username'}), 404
    return response


@login_required
@perm_api_blueprint.route('/api/user', methods=['GET'])
def get_user():
    if current_user.is_authenticated:
        return make_response(jsonify({'result': current_user.to_json()}))

    return make_response(jsonify({'message': 'Not logged in'})), 401


@perm_api_blueprint.route('/api/user-roles', methods=['GET'])
def getall_usertypes():
    items = list()
    for row in Roles.query.all():
        items.append(row.to_json())

    response = jsonify({'data': items})
    return response


@perm_api_blueprint.route('/api/user-roles/create', methods=['POST'])
def usertype_create():
    name = request.form['name']
    item = Roles()
    item.name = name

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'Role added', 'Role Data': item.to_json()})
    return response


@perm_api_blueprint.route('/api/user-role/<id>', methods=['GET'])
def usertype_get(id):
    item = Roles.query.filter_by(id=id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find a role'}), 404
    return response


@perm_api_blueprint.route('/api/page-alloc/create', methods=['POST'])
def page_allocate_create():
    route = request.form['route']
    name = request.form['name']
    image = request.form['image']
    psection = request.form['psection']
    ssection = request.form['ssection']
    pposition = request.form['pposition']
    sposition = request.form['sposition']

    item = Pageallocation()
    item.route = route
    item.name = name
    item.image = image
    item.psection = psection
    item.ssection = ssection
    item.pposition = pposition
    item.sposition = sposition

    db.session.add(item)
    db.session.commit()
    response = jsonify({'message': 'saved successfully'}), 200
    return response


@perm_api_blueprint.route('/api/department/create', methods=['POST'])
def staff_structure():
    name = request.form['name']

    item = Staffstructure()
    item.name = name

    db.session.add(item)
    db.session.commit()
    response = jsonify({'message': 'saved successfully'}), 200
    return response


@perm_api_blueprint.route('/api/get-staff/<id>', methods=['GET'])
def staff_get_id(id):
    item = Staffstructure.query.filter_by(id=id).first()
    # .query.filter_by(id=id).all()
    if item is not None:
        print(item.to_json)
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find any staff'}), 404
    return response


@perm_api_blueprint.route('/api/department', methods=['GET'])
def staff_get():
    data = []
    for row in Staffstructure.query.all():
        data.append(row.to_json())

    response = jsonify(data)
    return response


@perm_api_blueprint.route('/api/pages', methods=['GET'])
def getall_pages():
    items = list()
    for row in Pageallocation.query.all():
        items.append(row.to_json())

    response = jsonify({'data': items})
    return response


@perm_api_blueprint.route('/api/primary-pages', methods=['GET'])
def get_p_pages():
    items = dict()
    item = Pageallocation.query.filter(Pageallocation.status == True).group_by(Pageallocation.psection).with_entities(
        Pageallocation.psection)
    for x, row in enumerate(item, start=1):
        items.update({x: row[0]})
    response = jsonify(items)
    return response


@perm_api_blueprint.route('/api/get-priv-pages/<section>/<user_id>', methods=['GET'])
def get_priv_pages(section, user_id):
    item = Userpriviledge.query.join(Pageallocation, Pageallocation.id == Userpriviledge.pageallocation_id).join(User,
                                                                                                                 User.id == Userpriviledge.user_id).filter(
        Pageallocation.psection == section, Pageallocation.status == True, Userpriviledge.user_id == user_id).order_by(
        Pageallocation.pposition).with_entities(Pageallocation.name, Userpriviledge.status, Userpriviledge.id)

    if item is not None:
        data = list()
        for row in item:
            data.append({'name': row[0], 'status': row[1], 'priv_id': row[2]})
        response = jsonify(data), 200
    else:
        response = jsonify({'message': 'No Subsections'}), 404
    return response


@perm_api_blueprint.route('/api/get-new-priv/<section>', methods=['GET'])
def get_new_priv(section):
    item = Pageallocation.query.outerjoin(Userpriviledge, Pageallocation.id == Userpriviledge.pageallocation_id).filter(
        Pageallocation.psection == section, Pageallocation.status == True,
        Userpriviledge.pageallocation_id == None).with_entities(Pageallocation.name, Pageallocation.route,
                                                                Pageallocation.id)

    if item is not None:
        data = list()
        for row in item:
            data.append({'name': row[0], 'route': row[1], 'page_id': row[2]})
        response = jsonify(data), 200
    else:
        response = jsonify({'message': 'No Subsections'}), 404
    return response


@perm_api_blueprint.route('/api/get-section-postion/<user_id>', methods=['GET'])
def get_pages_sections(user_id):
    # TODO hardcode infuture will implement to make dynamic after the login page implemented
    raw_query = f"SELECT DISTINCT pageallocation.psection, pageallocation.pposition AS pageallocation_pposition, (SELECT count(p.id) FROM pageallocation p where p.psection = pageallocation.psection) AS countP FROM pageallocation JOIN userpriviledge ON pageallocation.id = userpriviledge.pageallocation_id WHERE pageallocation.status IS true AND userpriviledge.status IS true AND userpriviledge.user_id = {user_id} ORDER BY pageallocation.psection"
    items = db.session.execute(raw_query)

    # items = Pageallocation.query.join(Userpriviledge).filter(Pageallocation.status.is_(True),
    #                                                          Userpriviledge.status.is_(True),
    #                                                          Userpriviledge.user_id == 3).order_by(Pageallocation.psection).with_entities(Pageallocation.psection.distinct(), Pageallocation.pposition)
    if items is not None:
        data = list()
        for x, row in enumerate(items, start=1):
            data.append({str(row[1]): row[0], "count": row[2]})
        response = jsonify(data), 200
    else:
        response = jsonify({'message': 'Not Pages to Find'}), 404
    return response


@perm_api_blueprint.route('/api/get-subsection/<user_id>/<section_id>')
def get_subsection(user_id, section_id):
    item = Userpriviledge.query.join(Pageallocation, Pageallocation.id == Userpriviledge.pageallocation_id).join(User,
                                                                                                                 User.id == Userpriviledge.user_id).filter(
        Pageallocation.psection == section_id, Pageallocation.status.is_(True),
        Userpriviledge.user_id == user_id).order_by(Pageallocation.sposition).with_entities(Pageallocation.name,
                                                                                            Userpriviledge.status,
                                                                                            Userpriviledge.id,
                                                                                            Pageallocation.image,
                                                                                            Pageallocation.route)
    if item is not None:
        data = list()
        for row in item:
            data.append({'sub_section_name': row[0], 'status': row[1], 'user_priv_id': row[2], 'image': row[3],
                         'route': row[4]})
        response = jsonify(data), 200
    else:
        response = jsonify({'message': 'Not Sub Section to Find'}), 404
    return response


@perm_api_blueprint.route('/api/relate-page/<section>', methods=['GET'])
def related_page(section):
    item = Pageallocation.query.filter(Pageallocation.psection == section).all()
    if item is not None:
        items = list()
        for row in item:
            items.append(row.to_json())
        response = jsonify({'data': items})
    else:
        response = jsonify({'message': 'Cannot find Sub Section'}), 404
    return response


@perm_api_blueprint.route('/api/getall-branch', methods=['GET'])
def getall_branchs():
    items = list()
    for row in Branch.query.all():
        items.append(row.to_json())

    response = jsonify({'results': items})
    return response


@perm_api_blueprint.route('/api/branch/create', methods=['POST'])
def branch_create():
    name = request.form['name']
    item = Branch()
    item.name = name

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'Branch added', 'branch': item.to_json()})
    return response


@perm_api_blueprint.route('/api/get-branch/<id>', methods=['GET'])
def branch_get(id):
    item = Branch.query.filter_by(id=id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find branch'}), 404
    return response


@perm_api_blueprint.route('/api/staff/create', methods=['POST'])
def staff_registration():
    code = request.form['staffcode']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    username = request.form['username']
    password = sha256_crypt.hash((str(request.form['password'])))
    gender = request.form['gender']
    department = request.form['department']
    branch = request.form['branch']
    address1 = request.form['address1']
    address2 = request.form['address2']
    address3 = request.form['address3']
    postalcode = request.form['postalcode']
    city = request.form['city']
    country = request.form['country']
    date_of_birth = request.form['date_of_birth']
    mobile = request.form['mobile']
    email = request.form['email']

    item = Staff()
    item.code = code
    item.department_id = department
    item.gender = gender
    item.date_of_birth = date_of_birth
    item.mobile = mobile
    item.username = username
    db.session.add(item)
    db.session.commit()

    # User Address
    item_add = Useraddress()
    item_add.address1 = address1
    item_add.address2 = address2
    item_add.address3 = address3
    item_add.city = city
    item_add.country = country
    item_add.postal_code = postalcode
    db.session.add(item_add)
    db.session.commit()

    result = item_add.to_json()
    insert_addr_id = result.get('id')

    # UserForm
    item_user = User()
    item_user.username = username
    item_user.email = email
    item_user.first_name = firstname
    item_user.last_name = lastname
    item_user.password = password
    item_user.address_id = insert_addr_id
    item_user.role_id = 2
    item_user.branch_id = branch

    db.session.add(item_user)
    db.session.commit()
    result = item_user.to_json()
    response = jsonify({'message': 'User added', 'result': result})

    # When User is created, Priviledges are set
    set_privilege(result.get('id'))
    return response


@perm_api_blueprint.route('/api/staff/get-staff', methods=['GET'])
def getall_staff():
    items = list()
    for row in Staff.query.all():
        items.append(row.to_json())

    response = jsonify({'results': items})
    return response


@perm_api_blueprint.route('/api/staff/get-staff/<id>', methods=['GET'])
def staff_get_id2(id):
    item = Staff.query.filter_by(id=id).first()
    # .query.filter_by(id=id).all()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find any staff'}), 404
    return response


@perm_api_blueprint.route('/api/staff/update-staff/<id>', methods=['PUT'])
def staff_put_id(id):
    item = Staff.query.filter_by(id=id).first()
    # .query.filter_by(id=id).all()
    if item is not None:
        item.full_name = request.form['full_name']
        db.session.add(item)
        db.session.commit()
        response = jsonify({'message': 'staff updated'})
    else:
        response = jsonify({'message': 'Cannot find any staff'}), 404
    return response


@perm_api_blueprint.route('/api/staff/delete-staff/<id>', methods=['DELETE'])
def staff_delete(id):
    item = Staff.query.filter_by(id=id).first()
    if item is not None:
        db.session.delete(item)
        db.session.commit()
        # response= jsonify(item.to_delete)
        response = jsonify({'message': 'Successfully deleted'})
    else:
        response = jsonify({'message': 'Cannot find branch'}), 404
    return response


@perm_api_blueprint.route('/api/gen-staff-code', methods=['GET'])
def gen_staff_code():
    item = Staff.query.order_by(Staff.id.desc()).first()
    if item is not None:
        data = item.to_json()
        code = '000' + str(data.get('id') + 1)
        return jsonify({'code': code})
    else:
        code = '0001'
        return jsonify({'code': code})


@perm_api_blueprint.route('/api/student/registration/', methods=['POST'])
def Student_registration():
    name = request.form['name']
    code = request.form['code']
    roll_number = request.form['roll_number']
    student_address = request.form['student_address']
    gender = request.form['gender']
    date_of_birth = request.form['date_of_birth']
    parent_name = request.form['parent_name']
    parent_address = request.form['parent_address']
    parent_mobile_number = request.form['parent_mobile_number']
    parent_landline = request.form['parent_landline']
    parent_email = request.form['parent_email']
    old_school_name = request.form['old_school_name']
    old_school_grade = request.form['old_school_grade']
    old_school_joined = request.form['old_school_joined']
    old_school_left = request.form['old_school_left']
    datetime = request.form['datetime']
    active = request.form['active']
    grade = request.form['grade']
    join_date = request.form['join_date']
    blood_group = request.form['blood_group']
    nationality = request.form['nationality']
    student_email = request.form['student_email']

    item_add = Studentregistration()

    item_add.name = name
    item_add.code = code
    item_add.roll_number = roll_number
    item_add.student_address = student_address
    item_add.gender = gender
    item_add.date_of_birth = date_of_birth
    item_add.parent_name = parent_name
    item_add.parent_address = parent_address
    item_add.parent_mobile_number = parent_mobile_number
    item_add.parent_landline = parent_landline
    item_add.parent_email = parent_email
    item_add.old_school_name = old_school_name
    item_add.old_school_grade = old_school_grade
    item_add.old_school_joined = old_school_joined
    item_add.old_school_left = old_school_left
    item_add.datetime = datetime
    if 'True' or 'true' in active:
        item_add.active = True
    else:
        item_add.active = False
    item_add.grade = grade
    item_add.join_date = join_date
    item_add.blood_group = blood_group
    item_add.nationality = nationality
    item_add.student_email = student_email
    # item_add.studentattendance =studentattendance
    db.session.add(item_add)
    db.session.commit()

    result = item_add.to_json()
    return result


@perm_api_blueprint.route('/api/get-student/<id>', methods=['GET'])
def student_get(id):
    item = Studentregistration.query.filter_by(id=id).first()
    if item is not None:
        response1 = jsonify(item.to_json())
    else:
        response1 = jsonify({'message': 'can not find Student'}), 404
    return response1


@perm_api_blueprint.route('/api/putstudentR/<id>', methods=['PUT'])
def st_put(id):
    item = Studentregistration.query.filter_by(id=id).first()
    if item is not None:
        name = request.form['name']
        code = request.form['code']
        roll_number = request.form['roll_number']
        student_address = request.form['student_address']
        gender = request.form['gender']
        date_of_birth = request.form['date_of_birth']
        parent_name = request.form['parent_name']
        parent_address = request.form['parent_address']
        parent_mobile_number = request.form['parent_mobile_number']
        parent_landline = request.form['parent_landline']
        parent_email = request.form['parent_email']
        old_school_name = request.form['old_school_name']
        old_school_grade = request.form['old_school_grade']
        old_school_joined = request.form['old_school_joined']
        old_school_left = request.form['old_school_left']
        datetime = request.form['datetime']
        active = request.form['active']
        grade = request.form['grade']
        join_date = request.form['join_date']
        blood_group = request.form['blood_group']
        nationality = request.form['nationality']
        student_email = request.form['student_email']

        item.name = name
        item.code = code
        item.roll_number = roll_number
        item.student_address = student_address
        item.gender = gender
        item.date_of_birth = date_of_birth
        item.parent_name = parent_name
        item.parent_address = parent_address
        item.parent_mobile_number = parent_mobile_number
        item.parent_landline = parent_landline
        item.parent_email = parent_email
        item.old_school_name = old_school_name
        item.old_school_grade = old_school_grade
        item.old_school_joined = old_school_joined
        item.old_school_left = old_school_left
        item.datetime = datetime
        item.active = active
        item.grade = grade
        item.join_date = join_date
        item.blood_group = blood_group
        item.nationality = nationality
        item.student_email = student_email
        db.seesion.update(item)

        db.session.commit()

        response = jsonify({"message": "updated student data"})
    else:
        response = jsonify({"message": "can not find student details"})
    return response


@perm_api_blueprint.route('/api/del-std/<id>', methods=['PUT'])
def student_delet(id):
    item = Studentregistration.query.filter_by(id=id).first()
    if item is not None:
        active = request.form['active']
        if 'false' or 'False' in active:
            item.active = False
        db.session.add(item)
        db.session.commit()
        response = jsonify({'message': 'deletion completed'})

    else:
        response = jsonify({'message': 'can not find Student'}), 404
    return response


##############################################################################


###studentattendance post


def check_attended(std_code):
    item = Studentattendance.query.filter_by(id=std_code).first()
    if item is not None:
        return True
    else:
        return False


@perm_api_blueprint.route('/api/std-attd/<std_code>', methods=['POST'])
def get_attendance(std_code):
    item = Studentattendance.query.filter_by(student_code=std_code).first()

    student_code = request.form['student_code']
    student_name = request.form['student_name']
    date = request.form['date']
    day = request.form['day']
    month = request.form['month']
    year = request.form['year']
    attendance = request.form['attendance']
    remarks = request.form['remarks']
    status = request.form['status']
    grade = request.form['grade']
    student_id = request.form['student_id']

    item = Studentattendance()

    item.student_code = student_code
    item.student_name = student_name
    item.date = date
    item.day = day
    item.month = month
    item.year = year
    item.attendance = attendance
    item.remarks = remarks
    if 'false' or 'False' in status:
        item.status = False
    item.grade = grade
    item.student_id = student_id

    check_bool = check_attended(std_code)
    if not check_bool:
        db.session.add(item)
        db.session.commit()

        result = item.to_json()
        return result
    else:
        return jsonify({'message': 'attendance already marked'})


@perm_api_blueprint.route('/api/get-studentattend/<id>', methods=['GET'])
def studentattend_get(id):
    item = Studentattendance.query.filter_by(id=id).first()
    if item is not None:
        response2 = jsonify(item.to_json())
    else:
        response2 = jsonify({'message': 'can not find Student'})
    return response2


@perm_api_blueprint.route('/api/put-studentA/<id>', methods=['PUT'])
def student_put(id):
    item = Studentattendance.query.filter_by(id=id).first()
    if item is not None:
        student_name = request.form['student_name']
        date = request.form['date']
        month = request.form['month']
        year = request.form['year']
        attendance = request.form['attendance']
        remarks = request.form['remarks']
        status = request.form['status']
        grade = request.form['grade']
        # student_id = request.form['student_id']
        item.student_name = student_name
        item.date = date
        item.month = month
        item.year = year
        item.attendance = attendance
        item.remarks = remarks
        if 'false' or 'False' in status:
            item.status = False
        item.grade = grade
        # item.student_id = student_id
        db.session.add(item)

        db.session.commit()
        response = jsonify({'message': 'updated'})
    else:
        response = jsonify({'message': 'not found student'})
    return response


############################################@@###############################
##studentfee

@perm_api_blueprint.route('/api/student/fee/', methods=['POST'])
def Student_fee():
    fee_type_id = request.form['fee_type_id']
    student_name = request.form['student_name']
    pay_date = request.form['pay_date']
    actual_amount = request.form['actual_amount']
    balance_amount = request.form['balance_amount']
    total_amount = request.form['total_amount']
    pay_amount = request.form['pay_amount']
    fine = request.form['fine']
    prefix = request.form['prefix']
    individual_receipt = request.form['individual_receipt']
    mode_of_pay = request.form['mode_of_pay']
    receipt_number = request.form['receipt_number']
    bank = request.form['bank']
    cheque_number = request.form['cheque_number']
    cheque_date = request.form['cheque_date']
    remark = request.form['remark']
    status = request.form['status']
    active = request.form['active']
    student_id = request.form['student_id']

    item = Studentfee()
    item.fee_type_id = fee_type_id
    item.student_name = student_name
    item.pay_date = pay_date
    item.actual_amount = actual_amount
    item.balance_amount = balance_amount
    item.total_amount = total_amount
    item.pay_amount = pay_amount
    item.fine = fine
    item.prefix = prefix
    item.individual_receipt = individual_receipt
    item.mode_of_pay = mode_of_pay
    item.receipt_number = receipt_number
    item.bank = bank
    item.cheque_number = cheque_number
    item.cheque_date = cheque_date
    item.remark = remark
    if 'True' or 'true' in status:
        item.status = True
    else:
        item.status = False
    if active is 'false' or 'False':
        item.active = False
    else:
        item.active = True
    item.student_id = student_id

    # check = check_stdpaid(id)
    # if not check:
    db.session.add(item)
    db.session.commit()
    result = item.to_json()
    return result


@perm_api_blueprint.route('/api/student/fee-details/<id>', methods=['GET'])
def studfee_get(id):
    item = Studentfee.query.filter_by(id=id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'can not find Student'})
    return response


@perm_api_blueprint.route('/api/student/putfee-details/<id>', methods=['PUT'])
def put_details(id):
    item = Studentfee.query.filter_by(id=id).first()
    if item is not None:
        fee_type_id = request.form['fee_type_id']
        student_name = request.form['student_name']
        pay_date = request.form['pay_date']
        actual_amount = request.form['actual_amount']
        balance_amount = request.form['balance_amount']
        total_amount = request.form['total_amount']
        pay_amount = request.form['pay_amount']
        fine = request.form['fine']
        prefix = request.form['prefix']
        individual_receipt = request.form['individual_receipt']
        mode_of_pay = request.form['mode_of_pay']
        receipt_number = request.form['receipt_number']
        bank = request.form['bank']
        cheque_number = request.form['cheque_number']
        cheque_date = request.form['cheque_date']
        remark = request.form['remark']
        status = request.form['status']
        active = request.form['active']
        student_id = request.form['student_id']

        item = Studentfee()
        item.fee_type_id = fee_type_id
        item.student_name = student_name
        item.pay_date = pay_date
        item.actual_amount = actual_amount
        item.balance_amount = balance_amount
        item.total_amount = total_amount
        item.pay_amount = pay_amount
        item.fine = fine
        item.prefix = prefix
        item.individual_receipt = individual_receipt
        item.mode_of_pay = mode_of_pay
        item.receipt_number = receipt_number
        item.bank = bank
        item.cheque_number = cheque_number
        item.cheque_date = cheque_date
        item.remark = remark
        if 'true' or 'True' in status:
            item.status = True
        else:
            item.status = False
        if 'false' or 'False' in active:
            item.active = False
        else:
            item.active = True
        item.student_id = student_id
        db.session.add(item)

        db.session.commit()
        response = jsonify({'message': 'updated'})
    else:
        response = jsonify({'message': 'not found student'})
    return response


@perm_api_blueprint.route('/api/del-stdf/<id>', methods=['PUT'])
def student_deletf(id):
    item = Studentfee.query.filter_by(id=id).first()
    if item is not None:
        active = request.form['active']
        if 'false' or 'False' in active:
            item.active = False
        db.session.add(item)
        db.session.commit()
        response = jsonify({'message': 'deletion completed'})

    else:
        response = jsonify({'message': 'can not find Student'}), 404
    return response


##########JATIN

@perm_api_blueprint.route('/api/user-role-delete/<id>', methods=['DELETE'])
def usertype_delete(id):
    item = Roles.query.filter_by(id=id).first()
    if item is not None:
        db.session.delete(item)
        db.session.commit()
        # response= jsonify(item.to_delete)
        response = jsonify({'message': 'Successfully deleted'})
    else:
        response = jsonify({'message': 'Cannot find a role'}), 404
    return response


@perm_api_blueprint.route('/api/user-role-update/<id>', methods=['PUT'])
def usertype_update(id):
    item = Roles.query.filter_by(id=id).first()
    if item is not None:
        name = request.form['name']
        item.name = name
        db.session.commit()
        response = jsonify({'message': 'Successfully updated'})
    else:
        response = jsonify({'message': 'Cannot find role'}), 404
    return response


@perm_api_blueprint.route('/api/delete-branch/<id>', methods=['DELETE'])
def branch_delete(id):
    item = Branch.query.filter_by(id=id).first()
    if item is not None:
        db.session.delete(item)
        db.session.commit()
        # response= jsonify(item.to_delete)
        response = jsonify({'message': 'Successfully deleted'})
    else:
        response = jsonify({'message': 'Cannot find branch'}), 404
    return response


@perm_api_blueprint.route('/api/update-branch/<id>', methods=['PUT'])
def branch_put(id):
    item = Branch.query.filter_by(id=id).first()
    if item is not None:
        name = request.form['name']
        # item = request.form['item']
        item.name = name
        # item.item = item
        db.session.commit()
        # response= jsonify(item.to_de)
        response = jsonify({'message': 'Successfully updated'})
    else:
        response = jsonify({'message': 'Cannot find branch'}), 404
    return


@perm_api_blueprint.route('/api/course/create', methods=['POST'])
def course_create():
    course_name = request.form['course_name']
    course_semester = request.form['course_semester']

    item = Course()
    item.course_name = course_name
    item.course_semester = course_semester

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'course added', 'course': item.to_json()})
    return response


@perm_api_blueprint.route('/api/course/update/<id>', methods=['PUT'])
def course_update(id):
    item = Course.query.filter_by(id=id).first()
    if item is not None:
        course_name = request.form['course_name']
        course_semester = request.form['course_semester']

        item.course_name = course_name
        item.course_semester = course_semester

        db.session.commit()
        # response= jsonify(item.to_de)
        response = jsonify({'message': 'Successfully updated'})
    else:
        response = jsonify({'message': 'Cannot find course'}), 404
    return response


# get
@perm_api_blueprint.route('/api/course/get/<id>', methods=['GET'])
def course_get(id):
    item = Course.query.filter_by(id=id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find course'}), 404
    return response


# getall
@perm_api_blueprint.route('/api/get-courses', methods=['GET'])
def getall_course():
    items = list()
    for row in Course.query.all():
        items.append(row.to_json())

    response = jsonify(items)
    return response


# Delete
@perm_api_blueprint.route('/api/course/delete/<id>', methods=['Delete'])
def delete_course(id):
    item = Course.query.filter_by(id=id).first()
    if item is not None:
        db.session.delete(item)
        db.session.commit()
        # response= jsonify(item.to_delete)
        response = jsonify({'message': 'Successfully deleted'})
    else:
        response = jsonify({'message': 'Cannot find course'}), 404
    return response


#########################################################################################################################
# subjects
@perm_api_blueprint.route('/api/subject-create', methods=['Post'])
def subject_create():
    name = request.form['name']
    course_id = request.form['course_id']

    item = Subjects()
    item.name = name
    item.course_id = course_id

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'subject added', 'subject': item.to_json()})
    return response


@perm_api_blueprint.route('/api/update/<id>', methods=['PUT'])
def sub_update(id):
    item = Subjects.query.filter_by(id=id).first()
    if item is not None:
        name = request.form['name']
        course_id = request.form['course_id']

        item.name = name
        item.course_id = course_id

        db.session.commit()
        # response= jsonify(item.to_de)
        response = jsonify({'message': 'Successfully updated'})
    else:
        response = jsonify({'message': 'Cannot find subject'}), 404
    return response


@perm_api_blueprint.route('/api/get/<id>', methods=['GET'])
def subject_get(id):
    item = Subjects.query.filter_by(id=id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find subject'}), 404
    return response


@perm_api_blueprint.route('/api/get-subjects', methods=['GET'])
def subject_all():
    items = list()
    for row in Subjects.query.join(Course, Course.id == Subjects.course_id).with_entities(Course.course_name,
                                                                                          Subjects.id, Subjects.name):
        items.append({'course_name': row[0], 'subject_name': row[2], 'subject_id': row[1]})

    response = jsonify(items)
    return response


@perm_api_blueprint.route('/api/sub/delete/<id>', methods=['DELETE'])
def subject_delete():
    item = Subjects.query.filter_by(id=id).first()
    if item is not None:
        db.session.delete(item)
        db.session.commit()
        response = jsonify({'message': 'Successfully deleted'})
    else:
        response = jsonify({'message': 'Cannot find subject'}), 404
    return response


##########################################################################################################################
# paper-creation
@perm_api_blueprint.route('/api/paper-create', methods=['Post'])
def paper_create():
    subject_id = request.form['subject_id']
    duration = request.form['duration']
    no_of_questions = request.form['no_of_questions']
    paper_no = request.form['paper_no']
    user_id = request.form['user_id']

    item = Paper_creation()

    item.subject_id = subject_id
    item.duration = duration
    item.no_of_questions = no_of_questions
    item.paper_no = paper_no
    item.user_id = user_id

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'paper created', 'paper-create': item.to_json()})
    return response


@perm_api_blueprint.route('/api/paper-get/<paper_id>', methods=['GET'])
def getbyid(paper_id):
    item = Paper_creation.query.filter_by(paper_id=paper_id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find paper'}), 404
    return response


@perm_api_blueprint.route('/api/paper-getall', methods=['GET'])
def getallpaper():
    items = list()
    for row in Paper_creation.query.all():
        items.append(row.to_json())

    response = jsonify({'results': items})
    return response


@perm_api_blueprint.route('/api/paper-update', methods=['PUT'])
def paper_update(id):
    item = Paper_creation.query.filter_by(id=id).first()
    if item is not None:
        paper_id = request.form['paper_id']
        subject_id = request.form['subject_id']
        duration = request.form['duration']
        no_of_questions = request.form['no_of_questions']
        paper_no = request.form['paper_no']
        # status = request.form['status']
        user_id = request.form['user_id']

        item.paper_id = paper_id
        item.subject_id = subject_id
        item.duration = duration
        item.no_of_questions = no_of_questions
        item.paper_no = paper_no
        # item.status=status
        item.user_id = user_id

        db.session.commit()
        # response= jsonify(item.to_de)
        response = jsonify({'message': 'Successfully updated'})
    else:
        response = jsonify({'message': 'Cannot find paper'}), 404
    return response


# question
@perm_api_blueprint.route('/api/ques/update/', methods=['PUT'])
def question_update():
    item = Questions.query.filter_by(id=id).first()
    if item is not None:
        question_id = request.form['question_id']
        paper_id = request.form['paper_id']
        question = request.form['question']
        question_order = request.form['question_order']
        points = request.form['points']
        correct_ans = request.form['correct_ans']

        item.question_id = question_id
        item.paper_id = paper_id
        item.question = question
        item.question_order = question_order
        item.points = points
        item.correct_ans = correct_ans

        db.session.commit()
        # response= jsonify(item.to_de)
        response = jsonify({'message': 'Successfully updated'})
    else:
        response = jsonify({'message': 'Cannot find question'}), 404
    return response


@perm_api_blueprint.route('/api/ques/get/<question_id>', methods=['GET'])
def getquesbyid(question_id):
    item = Questions.query.filter_by(question_id=question_id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find subject'}), 404
    return response


@perm_api_blueprint.route('/api/ques/getall', methods=['GET'])
def getallques():
    items = list()
    for row in Questions.query.all():
        items.append(row.to_json())

    response = jsonify({'results': items})
    return response


##########################################################################################################################


@perm_api_blueprint.route('/api/ans/update/<answer_id>', methods=['PUT'])
def answer_update(answer_id):
    item = Answers.query.filter_by(id=id).first()
    if item is not None:
        answer_id = request.form['answer_id']
        question_id = request.form['question_id']
        answer = request.form['answer']
        answer_order = request.form['answer_order']

        item.question_id = question_id
        item.answer_id = answer_id
        item.answer = answer
        item.answer_order = answer_order

        db.session.commit()
        response = jsonify({'message': 'Successfully updated'})
    else:
        response = jsonify({'message': 'Cannot find question'}), 404
    return response


@perm_api_blueprint.route('/api/ans/get/<answer_id>', methods=['GET'])
def get_ans_byID(answer_id):
    item = Answers.query.filter_by(answer_id=answer_id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find subject'}), 404
    return response


@perm_api_blueprint.route('/api/ans/getall', methods=['GET'])
def getall_ans():
    items = list()
    for row in Answers.query.all():
        items.append(row.to_json())

    response = jsonify({'results': items})
    return response


########################################################################################################################
# exambooking
@perm_api_blueprint.route('/api/exm-book/create/', methods=['POST'])
def exm_book():
    # id = request.form['id']
    exam_id = request.form['exam_id']
    student_id = request.form['student_id']
    subject_id = request.form['subject_id']
    exam_date = request.form['exam_date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    user_id = request.form['user_id']

    item = Exambooking()
    # item.id = id
    item.exam_id = exam_id
    item.student_id = student_id
    item.subject_id = subject_id
    item.exam_date = exam_date
    item.start_time = start_time
    item.end_time = end_time
    item.user_id = user_id

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'Exam-booking created', 'Exam-booking': item.to_json()})
    return response


@perm_api_blueprint.route('/api/exm-book/get/<id>', methods=['GET'])
def getexambook(id):
    item = Exambooking.query.filter_by(id=id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find exam'}), 404
    return response


@perm_api_blueprint.route('/api/exm-book/getall', methods=['GET'])
def getexambookall():
    items = list()
    for row in Exambooking.query.all():
        items.append(row.to_json())

    response = jsonify({'results': items})
    return response


@perm_api_blueprint.route('/api/exm-book/delete/<id>', methods=['DELETE'])
def deleteexm(id):
    item = Exambooking.query.filter_by(id=id).first()
    if item is not None:
        db.session.delete(item)
        db.session.commit()
        # response= jsonify(item.to_delete)
        response = jsonify({'message': 'Successfully deleted'})
    else:
        response = jsonify({'message': 'Cannot find exam'}), 404
    return response


########################################################################################################################
# examresult
@perm_api_blueprint.route('/api/exm-result/create', methods=['POST'])
def examresult():
    student_id = request.form['student_id']
    exam_id = request.form['exam_id']
    exam_log = request.form['exam_log']
    results = request.form['results']
    marks = request.form['marks']
    # id =  request.form['id']

    item = Examresults()
    # item.id = id
    item.student_id = student_id
    item.exam_id = exam_id
    item.exam_log = exam_log
    item.results = results
    item.marks = marks

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'Exam-result created', 'Exam-result': item.to_json()})
    return


@perm_api_blueprint.route('/api/exm-result/get/<id>', methods=['GET'])
def getresult(id):
    item = Examresults.query.filter_by(id=id).first()
    if item is not None:
        response = jsonify(item.to_json())
    else:
        response = jsonify({'message': 'Cannot find result'}), 404
    return response


@perm_api_blueprint.route('/api/exm-result/getall', methods=['GET'])
def getresultall():
    items = list()
    for row in Examresults.query.all():
        items.append(row.to_json())

    response = jsonify({'results': items})
    return response


@perm_api_blueprint.route('/api/register-priv/<page_id>', methods=['GET'])
def register_priv(page_id):
    for row in User.query.filter(User.status == True).all():
        user_id = row.to_json().get('id')

        User.query
        items = Userpriviledge()
        items.user_id = user_id
        items.pageallocation_id = page_id
        items.status = False
        db.session.add(items)
        db.session.commit()
    return jsonify({'message': 'Successfully inserted'}), 200


@perm_api_blueprint.route('/api/update-priv/<id>/<status>', methods=['GET'])
def update_priv(id, status):
    if 'False' in status or 'false' in status:
        status = False
    else:
        status = True

    item = Userpriviledge.query.filter_by(id=id).first()
    item.status = status
    db.session.commit()
    return jsonify({'message': 'Updated Successfully'}), 200


@perm_api_blueprint.route('/api/gen-paper-code', methods=['GET'])
def gen_paper_code():
    item = Paper_creation.query.order_by(Paper_creation.paper_id.desc()).first()
    if item is not None:
        data = item.to_json()
        code = '000' + str(data.get('paper_id') + 1)
        return jsonify({'code': code})
    else:
        code = '0001'
        return jsonify({'code': code})


@perm_api_blueprint.route('/api/load-paper', methods=['GET'])
def load_paper():
    item = Paper_creation.query.filter(Paper_creation.status == True).all()
    if item is not None:
        data = list()
        for row in item:
            data.append(row.to_json())
        return jsonify({'data': data})
    else:
        return jsonify({'message': 'Cannot find result'}), 404


@perm_api_blueprint.route('/api/get-paper-detail/<paper_no>', methods=['GET'])
def get_paper_detail(paper_no):
    item = Paper_creation.query.join(Subjects, Subjects.id == Paper_creation.subject_id).join(Course,
                                                                                              Course.id == Subjects.course_id).filter(
        Paper_creation.paper_no == paper_no, Paper_creation.status == True).with_entities(Subjects.name,
                                                                                          Course.course_name,
                                                                                          Paper_creation.no_of_questions,
                                                                                          Paper_creation.paper_id)
    if item is not None:
        items = dict()
        for row in item:
            items.update({'subject_name': row[0], 'course_name': row[1], 'noofquestion': row[2], 'paperid': row[3]})
        response = jsonify(items), 200
        return response

    response = jsonify({'message': 'Cannot find result'}), 400
    return response


@perm_api_blueprint.route('/api/load-questions/<paper_id>', methods=['GET'])
def get_questions(paper_id):
    item = Questions.query.filter(Questions.paper_id == paper_id).all()
    data = list()
    for row in item:
        data.append(row.to_json())
    return jsonify(data), 200


@perm_api_blueprint.route('/api/get-question/<paper_id>/<question_ord>', methods=['GET'])
def get_question(paper_id, question_ord):
    item = Questions.query.filter(Questions.paper_id == paper_id, Questions.question_order == question_ord).all()
    data = list()
    for row in item:
        data.append(row.to_json())
    return jsonify(data), 200


@perm_api_blueprint.route('/api/get-answers/<question_id>', methods=['GET'])
def get_answers(question_id):
    item = Answers.query.filter(Answers.question_id == question_id).order_by(Answers.answer_order).all()
    data = list()
    for row in item:
        data.append(row.to_json())
    return jsonify(data), 200


@perm_api_blueprint.route('/api/get-total-question/<paper_id>', methods=['GET'])
def get_count_question(paper_id):
    item = Questions.query.filter(Questions.paper_id == paper_id).count()

    return jsonify({'count': item}), 200


@perm_api_blueprint.route('/api/paper-publish/<paper_id>', methods=['GET'])
def publish_paper(paper_id):
    item = Paper_creation.query.filter(Paper_creation.paper_id == paper_id).first()
    item.status = False
    db.session.commit()
    return jsonify({'message': 'Updated Successfully'}), 200


@perm_api_blueprint.route('/api/update-question', methods=['POST'])
def update_question():
    question = request.form['question']
    answer = request.form['answer']
    id = request.form['id']
    item = Questions.query.filter(Questions.question_id == id).first()
    item.question = question
    item.correct_ans = answer

    db.session.commit()
    return jsonify({'message': 'Updated Successfully'}), 200


@perm_api_blueprint.route('/api/delete-answers/<question_id>', methods=['GET'])
def delete_answers(question_id):
    item = Answers.query.filter(Answers.question_id == question_id).first()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'delete Successfully'}), 200


@perm_api_blueprint.route('/api/answer/create', methods=['POST'])
def answer_create():
    question_id = request.form['question_id']
    answer = request.form['answer']
    answer_order = request.form['answer_order']

    item = Answers()

    item.question_id = question_id
    item.answer = answer
    item.answer_order = answer_order

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'Answer created', 'Answer': item.to_json()})
    return response


@perm_api_blueprint.route('/api/question/create', methods=['POST'])
def question_create():
    paper_id = request.form['paper_id']
    question = request.form['question']
    question_order = request.form['question_order']
    points = request.form['points']
    correct_ans = request.form['correct_ans']

    item = Questions()

    item.paper_id = paper_id
    item.question = question
    item.question_order = question_order
    item.points = points
    item.correct_ans = correct_ans

    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': 'Question created', 'questions': item.to_json()})
    return response


@perm_api_blueprint.route('/api/student-recommendation/recommendation', methods=['POST'])
def recommendation():

    recommendation = request.form['recommendation']

    item = Recommendation()


    tags_In_Articles = {'AIS': [

        ['MATH', 'ALGORITHM', 'EQUATIONS', 'DATA'],

        ['MATH', 'IMAGEPROCESSING', 'ALGORITHM']

    ],

        'SE': [

            ['API', 'WEB', 'SOFTWARE','DEVOPS'],

            ['API', 'DEVELOPEMENT', 'WEB' , 'UNIX']

        ],

        'DSA': [

            ['DATA', 'GRAPH', 'VISUALIZATION', 'API'],

            ['DATA', 'VISUALIZATION']

        ],
        'AIMS': [

            ['DATA', 'MANAGEMENT', 'BUISINESS'],

            ['MANAGEMENT', 'ALGORITHM']

        ],
        'ISM': [

            ['PROJECT', 'MANAGEMENT', 'AGILE'],

            ['AGILE', 'MANAGEMENT', 'BUISINESS']

        ],
        'CS': [

            ['SECURITY', 'UNIX', 'HACKING', 'HACK'],

            ['SECURITY', 'UNIX', 'HACK']

        ]

    }

    article = recommendation.split()

    article = [x.upper() for x in article]

    NBClass = MultinomialNB(tags_In_Articles)

    OPPrediction = NBClass.predict(article)

    maxVal = -100000000000000000000000

    opSub = ''

    for key in OPPrediction.keys():

        if OPPrediction[key] > maxVal:
            opSub = key
            maxVal = OPPrediction[key]

    #OPPrediction = {k: v for k, v in sorted(OPPrediction.items(), key=lambda item: item[1])}

    #dict(sorted(OPPrediction.items(), key=lambda item: item[1]))
    #OPPrediction = sorted(OPPrediction.items(), key=lambda x: x[1])

    #response = jsonify({'message': list(OPPrediction.keys())[0]})

    item.recommendation = recommendation
    item.output = opSub
    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': opSub})

    return response



@perm_api_blueprint.route('/api/student-recommendation/feedback', methods=['POST'])
def feedback():

    feedback = request.form['feedback']
    dataset = pd.read_excel("/Users/fashaan/Documents/Programming/ActionLearning/user_service/resource/DataSet_NLP.xlsx")
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('stopwords')
    ###################################################################################
    corpus = []
    corpus2 = []
    for i in range(0, 11):
        corpus.append(NLP.commonFunc(dataset['Experience'][i]))
    print(corpus)
    ##############################################################################
    #testing = 'Teachers were good'
    stopwordsRemoved = NLP.commonFunc(feedback)
    corpus2.append(stopwordsRemoved)
    ##############################################################################
    cv = CountVectorizer(max_features=1500)
    X = cv.fit_transform(corpus).toarray()
    y = dataset.iloc[:, -1].values
    toTest = cv.transform(corpus2).toarray()

    classifier = GaussianNB()
    classifier.fit(X, y)
    y_pred = classifier.predict(toTest)

    item = Feedback()
    item.feedback = stopwordsRemoved
    item.output = int(y_pred[0])
    db.session.add(item)
    db.session.commit()

    response = jsonify({'message': int(y_pred[0])})

    return response


@perm_api_blueprint.route('/api/student-recommendation/get-report/<op>', methods=['GET'])
def getall_report(op):
    item = Feedback.query.filter(Feedback.output == op ).all()
    if item is not None:
        items = list()
        for row in item:
            items.append(row.to_json())
        response = jsonify({'data': items})
    else:
        response = jsonify({'message': 'Cannot find Sub Section'}), 404
    return response