from application import create_app, db
from application import models
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)
# initalize commands below
# run in terminal this command :: flask db init
# then need to run this command:: flask db upgrade

"""
Note: if you are adding more models later, use this cmd
flask db migrate
flask db upgrade 

for flask session disabling [visit this]
https://flask-login.readthedocs.io/en/latest/#disabling-session-cookie-for-apis
"""
from flask import g
from flask.sessions import SecureCookieSessionInterface
from flask_login import user_loaded_from_header


class CustomSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session from API requests."""

    def save_session(self, *args, **kwargs):
        if g.get('login_via_header'):
            return
        return super(CustomSessionInterface, self).save_session(*args,
                                                                **kwargs)


app.session_interface = CustomSessionInterface()


@user_loaded_from_header.connect
def user_loaded_from_header(self, user=None):
    g.login_via_header = True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
