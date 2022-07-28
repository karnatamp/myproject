import requests
from flask import session, request

class StudiesClient:

    @staticmethod
    def course_reg(form):
        payload = {
            'course_name': form.cname.data,
            'course_semester': form.semester.data
        }
        url = ' http://127.0.0.1:5002/api/course/create'
        response = requests.request("POST", url=url, data=payload)
        return response

    @staticmethod
    def subject_reg(form):
        payload = {
            'name': form.subject.data,
            'course_id': form.course.data
        }
        url = ' http://127.0.0.1:5002/api/subject-create'
        response = requests.request("POST", url=url, data=payload)
        return response

    @staticmethod
    def get_all_courses():
        r = requests.get(f'http://127.0.0.1:5002/api/get-courses')
        return r.json()

    @staticmethod
    def get_all_subjects():
        r = requests.get(f'http://127.0.0.1:5002/api/get-subjects')
        return r.json()

    @staticmethod
    def get_nextPaper_code():
        r = requests.get(f'http://127.0.0.1:5002/api/gen-paper-code')
        return r.json()

    @staticmethod
    def post_reg_paper(form):
        user_id = session['user'].get('id')
        payload = {
            'paper_no': form.papercode.data,
            'subject_id': form.subject.data,
            'no_of_questions': form.noquestion.data,
            'duration': form.duration.data,
            'user_id': user_id
        }
        url = ' http://127.0.0.1:5002/api/paper-create'
        response = requests.request("POST", url=url, data=payload)
        return response

    @staticmethod
    def get_papers():
        r = requests.get(f'http://127.0.0.1:5002/api/load-paper')
        return r.json()

    @staticmethod
    def get_paper_detail(paper_no):
        r = requests.get(f'http://127.0.0.1:5002/api/get-paper-detail/{paper_no}')
        return r.json()

    @staticmethod
    def load_questions(paper_id):
        r = requests.get(f'http://127.0.0.1:5002/api/load-questions/{paper_id}')
        return r.json()

    @staticmethod
    def get_question(paper_id, question_ord):
        r = requests.get(f'http://127.0.0.1:5002/api/get-question/{paper_id}/{question_ord}')
        return r.json()

    @staticmethod
    def get_answer(question_id):
        r = requests.get(f'http://127.0.0.1:5002/api/get-answers/{question_id}')
        return r.json()

    @staticmethod
    def get_count_answer(paper_id):
        r = requests.get(f'http://127.0.0.1:5002/api/get-total-question/{paper_id}')
        return r.json()

    @staticmethod
    def publis_paper(paper_id):
        r = requests.get(f'http://127.0.0.1:5002/api/paper-publish/{paper_id}')
        return r.json()


    @staticmethod
    def update_question(question, answer, id):
        payload = {
            'question': question,
            'answer': answer,
            'id': id
        }
        url = ' http://127.0.0.1:5002/api/update-question'
        response = requests.request("POST", url=url, data=payload)
        return response

    @staticmethod
    def delete_answer(question_id):
        r = requests.get(f'http://127.0.0.1:5002/api/delete-answers/{question_id}')
        return r.json()

    @staticmethod
    def insert_answer(question, answer, answer_order):
        payload = {
            'question_id': question,
            'answer': answer,
            'answer_order': answer_order
        }
        url = ' http://127.0.0.1:5002/api/answer/create'
        response = requests.request("POST", url=url, data=payload)
        return response

    @staticmethod
    def insert_question(paper_id, question, question_order,points,correct_ans):
        payload = {
            'paper_id': paper_id,
            'question': question,
            'question_order': question_order,
            'points': points,
            'correct_ans': correct_ans,
        }
        url = ' http://127.0.0.1:5002/api/question/create'
        response = requests.request("POST", url=url, data=payload)
        return response