from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('login')

class UserForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    roles = StringField('roles', validators=[DataRequired()])
    branch = StringField('branch', validators=[DataRequired()])
    address1 = StringField('address1', validators=[DataRequired()])
    address2 = StringField('address2', validators=[DataRequired()])
    address3 = StringField('address3', validators=[DataRequired()])
    postalcode = StringField('postalcode', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    country = StringField('country', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class BranchForm(FlaskForm):
    bname = StringField('bname', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class RolesForm(FlaskForm):
    rolename = StringField('rolename', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class DepartmentForm(FlaskForm):
    dname = StringField('dname', validators=[DataRequired()])
    submit = SubmitField('submitReg')


class StaffForm(FlaskForm):
    staffcode = StringField('staffcode', validators=[DataRequired()])
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    gender = StringField('gender', validators=[DataRequired()])
    dob = StringField('dob', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    phone = StringField('phone', validators=[DataRequired()])
    department = StringField('department', validators=[DataRequired()])
    branch = StringField('branch', validators=[DataRequired()])
    address1 = StringField('address1', validators=[DataRequired()])
    address2 = StringField('address2', validators=[DataRequired()])
    address3 = StringField('address3', validators=[DataRequired()])
    postalcode = StringField('postalcode', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    country = StringField('country', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class CourseForm(FlaskForm):
    cname = StringField('cname', validators=[DataRequired()])
    semester = StringField('semester', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class SubjectForm(FlaskForm):
    course = StringField('course', validators=[DataRequired()])
    subject = StringField('subject', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class PaperForm(FlaskForm):
    papercode = StringField('papercode', validators=[DataRequired()])
    subject = StringField('subject', validators=[DataRequired()])
    duration = StringField('duration', validators=[DataRequired()])
    noquestion = StringField('noquestion', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class RecommendationForm(FlaskForm):
    recommendation = StringField('recommendation', validators=[DataRequired()])
    submit = SubmitField('submitReg')

class FeedbackForm(FlaskForm):
    feedback = StringField('feedback', validators=[DataRequired()])
    submit = SubmitField('submitReg')
