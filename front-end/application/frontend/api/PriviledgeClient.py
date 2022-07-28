import requests

class PrivilegeClient:
    @staticmethod
    def group_sections(user_id):
        r = requests.get(f'http://127.0.0.1:5002/api/get-section-postion/{user_id}')
        sections = r.json()
        return sections

    @staticmethod
    def get_sub_sections(user_id, section_id):
        r = requests.get(f'http://127.0.0.1:5002/api/get-subsection/{user_id}/{section_id}')
        sub_sections = r.json()
        return sub_sections

    @staticmethod
    def get_primary_section():
        r = requests.get(f'http://127.0.0.1:5002/api/primary-pages')
        return r.json()

    @staticmethod
    def get_priv_pages(section, user_id):
        r = requests.get(f'http://127.0.0.1:5002/api/get-priv-pages/{section}/{user_id}')
        return r.json()

    @staticmethod
    def get_new_pages_not_set(section):
        r = requests.get(f'http://127.0.0.1:5002/api/get-new-priv/{section}')
        return r.json()

    @staticmethod
    def post_insert_priv(page_id):
        r = requests.get(f'http://127.0.0.1:5002/api/register-priv/{page_id}')
        return r.json()

    @staticmethod
    def update_page(id, status):
        r = requests.get(f'http://127.0.0.1:5002/api/update-priv/{id}/{status}')
        return r.json()