from . import db
import datetime as dt
from datetime import datetime
from flask_login import UserMixin
from passlib.hash import sha256_crypt

import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB


class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True)
    user = db.relationship('User', uselist=False, backref="roles")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), unique=False, nullable=False)
    last_name = db.Column(db.String(255), unique=False, nullable=False)
    password = db.Column(db.String(255), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True)
    api_key = db.Column(db.String(255), unique=True, nullable=True)
    date_reg = db.Column(db.DateTime, default=dt.datetime.utcnow, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('useraddress.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    userpriv = db.relationship('Userpriviledge', uselist=False, backref="User")
    paper_id = db.relationship('Paper_creation', uselist=False, backref="User")

    def encode_api_key(self):
        self.api_key = sha256_crypt.hash(self.username + str(datetime.utcnow))

    def encode_password(self):
        self.password = sha256_crypt.hash(self.password)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def to_json(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'id': self.id,
            'api_key': self.api_key,
            'is_active': True,
            'is_admin': self.is_admin
        }


class Useraddress(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address1 = db.Column(db.String(255), unique=False, nullable=False)
    address2 = db.Column(db.String(255), unique=False, nullable=True)
    address3 = db.Column(db.String(255), unique=False, nullable=True)
    city = db.Column(db.String(100), unique=False, nullable=False)
    country = db.Column(db.String(100), unique=False, nullable=False)
    postal_code = db.Column(db.String(100), unique=False, nullable=False)
    user = db.relationship('User', uselist=False, backref="useraddress")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'address1': self.address1,
            'address2': self.address2,
            'address3': self.address3,
            'city': self.city,
            'country': self.country,
            'postal_code': self.postal_code,
        }


class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True)
    user = db.relationship('User', uselist=False, backref="branch")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'branch_id': self.id,
            'branch_name': self.name
        }


class Pageallocation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route = db.Column(db.String(255), unique=False, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    image = db.Column(db.String(255), unique=False, nullable=True)
    psection = db.Column(db.String(100), unique=False, nullable=False)
    ssection = db.Column(db.String(100), unique=False, nullable=False)
    pposition = db.Column(db.Integer, unique=False, nullable=False)
    sposition = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True)
    userpriv = db.relationship('Userpriviledge', uselist=False, backref="pageallocation")

    def __repr__(self):
        return '<route {}>'.format(self.route)

    def to_json(self):
        return {
            'id': self.id,
            'route': self.route,
            'name': self.name,
            'image': self.image,
            'psection': self.psection,
            'ssection': self.ssection,
            'pposition': self.pposition,
            'sposition': self.sposition
        }


class Userpriviledge(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pageallocation_id = db.Column(db.Integer, db.ForeignKey('pageallocation.id'), nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'page_id': self.pageallocation_id
        }


class Course(db.Model):
    course_name = db.Column(db.String(100), unique=False, nullable=False)
    course_semester = db.Column(db.String(100), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subfk = db.relationship('Subjects', uselist=False, backref="course")

    def __repr__(self):
        return '<status {}>'.format(self.status)

    def to_json(self):
        return {
            'course_name': self.course_name,
            'course_semester': self.course_semester,
            'status': self.status,
            'id': self.id
        }


class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'name': self.name,
            'status': self.status
        }


class Staffstructure(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True)
    staff_relation = db.relationship('Staff', uselist=False, backref="staffstructure")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    gender = db.Column(db.String(255), unique=False, nullable=True)
    date_of_birth = db.Column(db.DateTime, nullable=True)
    mobile = db.Column(db.String(255), unique=False, nullable=True)
    joining_date = db.Column(db.DateTime, default=dt.datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    department_id = db.Column(db.Integer, db.ForeignKey('staffstructure.id'), nullable=False)

    def __repr__(self):
        return '<id %r>' % (self.id)

    def to_json(self):
        return {
            'id': self.id,
            'is_active': True,
            'gender': self.gender,
            'mobile': self.mobile,
            'department_id': self.department_id,
            'username': self.username
        }


class Studentregistration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    roll_number = db.Column(db.String(100), unique=True, nullable=False)
    student_address = db.Column(db.String(100), unique=False, nullable=False)
    studentusername = db.Column(db.String(100), unique=True, nullable=False)
    gender = db.Column(db.String(15), unique=False, nullable=False)
    date_of_birth = db.Column(db.String(20), unique=False, nullable=False)
    parent_name = db.Column(db.String(100), unique=False, nullable=False)
    parent_mobile_number = db.Column(db.String(15), unique=False, nullable=False)
    parent_email = db.Column(db.String(30), unique=False, nullable=True)
    active = db.Column(db.Boolean, default=True, unique=False, nullable=False)
    join_date =  db.Column(db.DateTime, default=dt.datetime.utcnow, nullable=False)
    student_email = db.Column(db.String(100), unique=True, nullable=False)
    exam_book = db.relationship('Exambooking', uselist=False, backref="studentregistration")
    exam_result = db.relationship('Examresults', uselist=False, backref="studentregistration")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'roll_number': self.roll_number,
            'student_address': self.student_address,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'parent_name': self.parent_name,
            'parent_address': self.parent_address,
            'parent_mobile_number': self.parent_mobile_number,
            'parent_landline': self.parent_landline,
            'parent_email': self.parent_email,
            'old_school_name': self.old_school_name,
            'old_school_grade': self.old_school_grade,
            'old_school_joined': self.old_school_joined,
            'old_school_left': self.old_school_left,
            'datetime': self.datetime,
            'active': self.active,
            'grade': self.grade,
            'join_date': self.join_date,
            'blood_group': self.blood_group,
            'nationality': self.nationality,
            'student_email': self.student_email
        }


class Studentattendance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_code = db.Column(db.String(100), unique=False, nullable=False)
    student_name = db.Column(db.String(100), unique=False, nullable=False)
    date = db.Column(db.DateTime, unique=False, nullable=False)
    day = db.Column(db.String(100), unique=False, nullable=False)
    month = db.Column(db.String(100), unique=False, nullable=False)
    year = db.Column(db.String(100), unique=False, nullable=False)
    attendance = db.Column(db.String(100), unique=False, nullable=False)
    remarks = db.Column(db.String(100), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True, unique=False, nullable=False)
    grade = db.Column(db.Integer, unique=False, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('studentregistration.id'), nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'student_code': self.student_code,
            'student_name': self.student_name,
            'student_id': self.student_id,
            'date': self.date,
            'day': self.day,
            'month': self.month,
            'year': self.year,
            'attendance': self.attendance,
            'remarks': self.remarks,
            'status': self.status,
            'grade': self.grade
        }


class Studentfee(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fee_type_id = db.Column(db.String(100), unique=True, nullable=False)
    student_name = db.Column(db.String(100), unique=False, nullable=False)
    pay_date = db.Column(db.DateTime, nullable=False)
    actual_amount = db.Column(db.FLOAT, unique=False, nullable=False)
    pay_amount = db.Column(db.FLOAT, unique=False, nullable=False)
    balance_amount = db.Column(db.FLOAT, unique=False, nullable=False)
    total_amount = db.Column(db.FLOAT, unique=False, nullable=False)
    fine = db.Column(db.FLOAT, unique=False, nullable=False)
    prefix = db.Column(db.String(100), unique=False, nullable=False)
    individual_receipt = db.Column(db.String(100), unique=False, nullable=False)
    receipt_number = db.Column(db.String(100), unique=False, nullable=False)
    mode_of_pay = db.Column(db.String(100), unique=False, nullable=False)
    bank = db.Column(db.String(100), nullable=False)
    cheque_number = db.Column(db.String(100), unique=True, nullable=False)
    cheque_date = db.Column(db.DateTime, nullable=False)

    remark = db.Column(db.String(100), unique=True, nullable=False)

    status = db.Column(db.Boolean, unique=False, nullable=False)
    active = db.Column(db.Boolean, unique=False, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('studentregistration.id'), nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'fee_type_id': self.fee_type_id,
            'student_name': self.student_name,
            'pay_date': self.pay_date,
            'actual_amount': self.actual_amount,
            'pay_amount': self.pay_amount,
            'balance_amount': self.balance_amount,
            'total_amount': self.total_amount,
            'fine': self.fine,
            'prefix': self.prefix,
            'individual_receipt': self.individual_receipt,
            'receipt_number': self.receipt_number,
            'mode_of_pay': self.mode_of_pay,
            'bank': self.bank,
            'cheque_number': self.cheque_number,
            'cheque_date': self.cheque_date,
            'remark': self.remark,
            'status': self.status,
            'active': self.active
        }


class Paper_creation(db.Model):
    paper_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    no_of_questions = db.Column(db.Integer, nullable=False)
    paper_no = db.Column(db.String(100), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    que_fk = db.relationship('Questions', uselist=False, backref="paper_creation")

    def __repr__(self):
        return '<paper_id {}>'.format(self.paper_id)

    def to_json(self):
        return {

            'paper_id': self.paper_id,
            'subject_id': self.subject_id,
            'duration': self.duration,
            'no_of_question': self.no_of_questions,
            'paper_no': self.paper_no,
            'status': self.status,
            'user_id': self.user_id
        }


class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper_creation.paper_id'), nullable=False)
    question = db.Column(db.Text())
    question_order = db.Column(db.Integer, default=True)
    points = db.Column(db.Float, unique=False, nullable=False)
    correct_ans = db.Column(db.Integer, default=True)
    status = db.Column(db.Boolean, default=True)
    ansfk = db.relationship('Answers', uselist=False, backref='questions')

    def __repr__(self):
        return '<question_id {}>'.format(self.question_id)

    def to_json(self):
        return {

            'question_id': self.question_id,
            'paper_id': self.paper_id,
            'question': self.question,
            'question_order': self.question_order,
            'points': self.points,
            'correct_ans': self.correct_ans,
            'status': self.status
        }


class Answers(db.Model):
    answer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    answer = db.Column(db.Text())
    answer_order = db.Column(db.Integer, default=True)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<answer_id {}>'.format(self.answer_id)

    def to_json(self):
        return {

            'answer_id': self.answer_id,
            'question_id': self.question_id,
            'answer': self.answer,
            'answer_order': self.answer_order,
            'status': self.status
        }


class Exambooking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.String, unique=True, default=True)
    student_id = db.Column(db.Integer, db.ForeignKey('studentregistration.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subfk = db.relationship('Examresults', uselist=False, backref="exambooking")

    # subfkk = db.relationship('Examresults', uselist=False, backref="Exam_booking")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {

            'id': self.id,
            'exam_id': self.exam_id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'exam_date': self.exam_date,
            'user_id': self.user_id
        }


class Examresults(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey('studentregistration.id'), nullable=False)
    exam_id = db.Column(db.String, db.ForeignKey('exambooking.exam_id'), nullable=False)
    exam_log = db.Column(db.Text())
    results = db.Column(db.String(100), unique=False, nullable=False)
    marks = db.Column(db.Float, unique=False, nullable=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {

            'student_id': self.student_id,
            'exam_id': self.exam_id,
            'exam_log': self.exam_log,
            'result': self.results,
            'marks': self.marks,
            'id': self.id
        }


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recommendation = db.Column(db.String(255), unique=False, nullable=True)
    output = db.Column(db.String(255), unique=False, nullable=True)

    def __repr__(self):
        return '<id %r>' % (self.id)

    def to_json(self):
        return {
            'recommendation': self.recommendation,
            'output': self.output

        }

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedback = db.Column(db.String(255), unique=False, nullable=True)
    output = db.Column(db.String(255), unique=False, nullable=True)

    def __repr__(self):
        return '<id %r>' % (self.id)

    def to_json(self):
        return {
            'feedback': self.feedback,
            'output': self.output

        }



class MultinomialNB:
    def __init__(self, articles_per_tag):
        self.alpha = 1
        self.priors_per_tag = {}
        self.likelyhood_per_word_per_tag = {}
        self.articles_per_tag = articles_per_tag
        self.tags = articles_per_tag.keys()
        self.train()

    def train(self):

        tag_counts_map = {tag: len(self.articles_per_tag[tag]) for tag in self.tags}  ### number of lists per tag

        self.priors_per_tag = {tag: tag_counts_map[tag] / sum(tag_counts_map.values()) for tag in
                               self.tags}  ## prob of lists globally

        self.likelyhood_per_word_per_tag = self.alternativeFunction()

    def predict(self, article):

        prob_per_tag = {tag: math.log(prior) for tag, prior in self.priors_per_tag.items()}

        for word in article:

            for tag in self.tags:

                if word in self.likelyhood_per_word_per_tag.keys():
                    prob_per_tag[tag] = prob_per_tag[tag] + math.log(self.likelyhood_per_word_per_tag[word][tag])

        return prob_per_tag

    ##############################################################################################################

    def alternativeFunction(self):

        wordFreq_perTag = {}

        totalWordsPerTag = {}

        for tag in self.tags:

            totalWordsPerTag[tag] = 0

            countVar = 0

            for article in self.articles_per_tag[tag]:

                for word in article:

                    countVar = countVar + 1

                    if word not in wordFreq_perTag.keys():

                        wordFreq_perTag[word] = {}

                        wordFreq_perTag[word][tag] = 1;

                    else:

                        if tag in wordFreq_perTag[word].keys():

                            wordFreq_perTag[word][tag] = wordFreq_perTag[word][tag] + 1;
                        else:
                            wordFreq_perTag[word][tag] = 1;

            totalWordsPerTag[tag] = countVar

        for val in wordFreq_perTag.keys():

            for tag in self.tags:

                if tag in wordFreq_perTag[val].keys():

                    wordFreq_perTag[val][tag] = (wordFreq_perTag[val][tag] + 1) / (totalWordsPerTag[tag] + 2)

                else:

                    wordFreq_perTag[val][tag] = 1 / (totalWordsPerTag[tag] + 2)

        return wordFreq_perTag

class NLP:

    def commonFunc(ipStr):
        review = re.sub('[^a-zA-Z]', ' ', ipStr)
        review = review.lower()
        review = review.split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        review = [ps.stem(word) for word in review if not word in set(all_stopwords)]
        review = ' '.join(review)

        return review