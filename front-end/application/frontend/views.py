import os

import requests
from jinja2 import ext

from . import forms
from . import frontend_blueprint
from .api.PriviledgeClient import PrivilegeClient
from .api.UserClient import UserClient
from .api.StaffClient import StaffClient
from .api.StudiesClient import StudiesClient
from .. import login_manager

from flask import render_template, session, redirect, url_for, flash, request, jsonify, make_response
from flask_login import current_user
import json


@login_manager.user_loader
def load_user(user_id):
    item = UserClient.get_user()
    return item.get('result')


def navigation_data(user_id):
    response_section = PrivilegeClient.group_sections(user_id)
    nav_bar = dict()
    for data in response_section:
        temp = list(data.values())
        response_sub_section = PrivilegeClient.get_sub_sections(user_id, temp[0])
        nav_bar.update({temp[0]: response_sub_section})
    return nav_bar


@frontend_blueprint.route('/dashboard', methods=['GET'])
def home():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))
    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    return render_template('dashboard/index.html', sections=nav_data)


@frontend_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated or (session.get('user') and len(session['user']) > 0):
        return redirect(url_for('frontend.home'))

    form = forms.LoginForm()
    if request.method == "POST":
        api_key = UserClient.post_login(form)
        if api_key:
            session['user_api_key'] = api_key
            user = UserClient.get_user()
            session['user'] = user['result']
            flash('Welcome back, ' + user['result']['username'], 'success')
            return jsonify({'status': 200})
        else:
            return jsonify({'status': 401})
    return render_template('login/index.html')


@frontend_blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('frontend.login'))


@frontend_blueprint.route('/user-reg', methods=['GET', 'POST'])
def user_register():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))
    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    branches = UserClient.get_branches()
    roles = UserClient.get_roles()

    form = forms.UserForm()
    if request.method == "POST":
        response_result = UserClient.post_user_reg(form)
        return jsonify({'status': response_result.status_code})

    return render_template('user/register.html', sections=nav_data, branches=branches, roles=roles)


@frontend_blueprint.route('/branch-create', methods=['GET', 'POST'])
def branch_register():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))
    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    form = forms.BranchForm()
    if request.method == "POST":
        response = UserClient.post_branch_reg(form)
        return jsonify({'status': response.status_code})

    return render_template('user/branch.html', sections=nav_data)


@frontend_blueprint.route('/user-roles', methods=['GET', 'POST'])
def user_roles():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    form = forms.RolesForm()
    if request.method == "POST":
        response_result = UserClient.roles(form)
        return jsonify({'status': response_result.status_code})

    return render_template('user/user-roles.html', sections=nav_data)

@frontend_blueprint.route('/staff-dep', methods=['GET','POST'])
def department_reg():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    form = forms.DepartmentForm()
    if request.method == "POST":
        response_result = StaffClient.department_reg(form)
        return jsonify({'status': response_result.status_code})

    return render_template('staff/department.html', sections=nav_data)


@frontend_blueprint.route('/staff-register', methods=['GET','POST'])
def staff_reg():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    branches = UserClient.get_branches()
    roles = UserClient.get_roles()
    departments = StaffClient.get_departments()
    staff_code = StaffClient.get_staff_latest_code().get('code')

    form = forms.StaffForm()
    if request.method == "POST":
        response_result = StaffClient.post_staff_reg(form)
        return jsonify({'status': response_result.status_code})

    return render_template('staff/staff_register.html', sections=nav_data, branches=branches, roles=roles, departments=departments, code=staff_code)

@frontend_blueprint.route('/set-priv', methods=['GET', 'POST'])
def set_priv():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    users = UserClient.get_all_users()
    return render_template('user/set_priviledge.html', sections=nav_data, users=users)

def process_load_privledge(user_id):
    pages = PrivilegeClient.get_primary_section()

    for key, value in pages.items():
        section_name = value
        data_not_set = PrivilegeClient.get_new_pages_not_set(section_name)
        if data_not_set:
            for row in data_not_set:
                page_id = row.get('page_id')
                PrivilegeClient.post_insert_priv(page_id)

    form_dict = dict()
    for key, value in pages.items():
        section_name = value
        data = PrivilegeClient.get_priv_pages(section_name, user_id)
        form_dict.update({section_name: data})

    return form_dict

@frontend_blueprint.route('/get-page-priv', methods=['POST'])
def get_page_priviledge():
    pages = PrivilegeClient.get_primary_section()
    user_id = request.form['user']
    if 'id' in request.form:
        id = request.form['id']
        sign = request.form['sign']
        PrivilegeClient.update_page(id, sign)

    response = process_load_privledge(user_id)

    return render_template('user/sub_load_pirv_page.html', pages=response, user_id=user_id)

@frontend_blueprint.route('/course-reg', methods=['GET','POST'])
def course_reg():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    form = forms.CourseForm()
    if request.method == "POST":
        response_result = StudiesClient.course_reg(form)
        return jsonify({'status': response_result.status_code})

    return render_template('studies/course.html', sections=nav_data)


@frontend_blueprint.route('/subject-reg', methods=['GET','POST'])
def subject_reg():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)
    courses = StudiesClient.get_all_courses()

    form = forms.SubjectForm()
    if request.method == "POST":
        response_result = StudiesClient.subject_reg(form)
        return jsonify({'status': response_result.status_code})

    return render_template('studies/subject.html', sections=nav_data, courses=courses)


@frontend_blueprint.route('/paper-create', methods=['GET','POST'])
def paper_create():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)
    subjects = StudiesClient.get_all_subjects()
    code = StudiesClient.get_nextPaper_code().get('code')

    form = forms.PaperForm()
    if request.method == 'POST':
        response_result = StudiesClient.post_reg_paper(form)
        return jsonify({'status': response_result.status_code})

    return render_template('studies/paper_creation.html', sections=nav_data, subjects=subjects, code=code)\


@frontend_blueprint.route('/question-bank', methods=['GET','POST'])
def question_bank():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)
    papers = StudiesClient.get_papers().get('data')


    return render_template('studies/create_questions.html', sections=nav_data, papers=papers)


@frontend_blueprint.route('/qbank', methods=['POST'])
def qbank():
    paperno = request.form['paperno']
    response = StudiesClient.get_paper_detail(paperno)

    return render_template('studies/qbank.html', paperno=paperno, paper_detail=response)

@frontend_blueprint.route('/imageuploader', methods=['POST'])
def imageuploader():
    file = request.files.get('file')
    if file:
        filename = file.filename.lower()
        if ext in ['jpg', 'gif', 'png', 'jpeg']:
            img_fullpath = os.path.join('application/static/images', filename)
            file.save(img_fullpath)
            return jsonify({'location' : filename})

    # fail, image did not upload
    output = make_response(404)
    output.headers['Error'] = 'Image failed to upload'
    return output

@frontend_blueprint.route('/loadQpad', methods=['POST'])
def loadQpad():
    paper_id = request.form['paper']
    noofquestion = request.form['noofquestion']

    questions = StudiesClient.load_questions(paper_id)
    question_list = list()
    for row in questions:
        question_list.append(row.get('question_order'))

    html_data = ''
    for i in range(1,int(noofquestion)+1):
        if i in question_list:
            html_data += f"<div class='col-sm-2' style='padding:1px 2px 1px 2px;'><button class='btn btn-primary' onclick='getQue({paper_id}, {i})'>{i}</button></div>"
        else:
            html_data += f"<div class='col-sm-2' style='padding: 1px 2px 1px 2px;'><button class='btn btn-default' onclick='getQue(0, {i})'>{i}</button></div>"

    return html_data


@frontend_blueprint.route('/get_que', methods=['POST'])
def get_que():
    paper = request.form['paper']
    que_ord = request.form['que']

    question_stack = list()
    question = StudiesClient.get_question(paper, que_ord)
    for row in question:
        question_stack.append(row.get('question'))
        question_stack.append(row.get('correct_ans'))
        question_id = row.get('question_id')
        result = StudiesClient.get_answer(question_id)
        for inrow in result:
            question_stack.append(inrow.get('answer'))

    return jsonify({'data':question_stack})

@frontend_blueprint.route('/totalnoquestion', methods=['POST'])
def total_no_question():
    paper = request.form['paper']

    get_count = StudiesClient.get_count_answer(paper).get('count')
    return jsonify({'count':get_count})


@frontend_blueprint.route('/confirm-publish-exam', methods=['POST'])
def publish_exam():
    paper = request.form['paper']

    response = StudiesClient.publis_paper(paper)
    return jsonify(response)


@frontend_blueprint.route('/save_ques', methods=['POST'])
def save_questions():
    data = [request.form['Pno'],request.form['question'],request.form['qnum'],request.form['correct'],request.form['ans1'],request.form['ans2'],request.form['ans3'],request.form['ans4']]
    result_question = StudiesClient.get_question(data[0], data[2])
    if len(result_question) > 0:
        for row in result_question:
            question_id = row.get('question_id')
            StudiesClient.update_question(data[1], data[3], question_id)
            StudiesClient.delete_answer(question_id)
            for i in range(1,5):
                answer = data[i+3]
                answer_ordr = i
                StudiesClient.insert_answer(question_id, answer, answer_ordr)
    else:
        paperid = data[0]
        question = data[1]
        question_order = data[2]
        correct = data[3]
        StudiesClient.insert_question(paperid, question, question_order, 1.0, correct)
        result_question = StudiesClient.get_question(data[0], data[2])

        for row in result_question:
            question_id = row.get('question_id')
            for i in range(1,5):
                answer = data[i+3]
                answer_ordr = i
                StudiesClient.insert_answer(question_id, answer, answer_ordr)

    return jsonify({'message':'Questions & Answers Saved'}), 200


@frontend_blueprint.route('/book-exam', methods=['GET','POST'])
def book_exam():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    return render_template('studies/book_exam.html', sections=nav_data)


@frontend_blueprint.route('/student-reg', methods=['GET','POST'])
def student_reg():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    return render_template('student/student_reg.html', sections=nav_data)


@frontend_blueprint.route('/recommendation', methods=['GET','POST'])
def recommendation():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    form = forms.RecommendationForm()
    if request.method == "POST":
        response_result = UserClient.recommendation(form)
        temp = json.loads(response_result.text)
        return jsonify({'status': response_result.status_code,'recommendedOp':temp.get('message')})

    return render_template('student_recommendation/recommendation.html', sections=nav_data)

@frontend_blueprint.route('/feedback', methods=['GET','POST'])
def feedback():
    if not session.get('user'):
        return redirect(url_for('frontend.login'))

    user_id = session['user'].get('id')
    nav_data = navigation_data(user_id)

    form = forms.FeedbackForm()
    if request.method == "POST":
        response_result = UserClient.feedback(form)
        return jsonify({'status': response_result.status_code})

    return render_template('student_recommendation/feedback.html', sections=nav_data)

