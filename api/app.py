import json
import flask
import requests
import os

from flask.ext.sqlalchemy import SQLAlchemy

import models

CLIENT_ID = '168912103717-ol5cm9u0m4mv292aboadb9arjl59g6to.apps.googleusercontent.com'

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+pysqlite:///sqlite.db'
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

def authenticated(function):
    def wrapper(*args, **kwargs):
        db_session = db.session()
        session_id = flask.session.get('session_id', -1)
        session = db_session.query(models.Session).get(session_id)
        if session:
            if session.valid:
                return function(session, *args, **kwargs)
            else:
                db_session.delete(session)
                db_session.commit()
        return flask.redirect(flask.url_for('splash'))
    wrapper.__name__ = function.__name__
    return wrapper

@app.route('/', methods=['GET'])
def splash():
    db_session = db.session()
    session_id = flask.session.get('session_id', -1)
    session = db_session.query(models.Session).get(session_id)
    if session and session.valid:
        return flask.redirect(flask.url_for('home'))
    return flask.render_template('splash.html')

@app.route('/home', methods=['GET'])
@authenticated
def home(session):
    return flask.render_template('home.html')

@app.route('/api/v1.0/tokensignin', methods=['POST'])
def api_tokensignin_1_0():
    id_token = flask.request.form.get('idtoken', '')
    if not id_token:
        return flask.abort(400, 'no url parameter matching idtoken')
    resp = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=%s' % (id_token,))
    if resp.status_code == requests.codes.OK:
        json_ = resp.json()
        if json_['aud'] == CLIENT_ID and json_['email_verified'] == 'true':
            user_id = json_['sub']
            db_session = db.session()
            user = db_session.query(models.User).filter_by(user_id=user_id).first()
            if not user:
                user = models.User(user_id=user_id, email=json_['email'])
                db_session.add(user)
            db_session.commit()
            session = models.Session(user_id=user.id)
            db_session.add(session)
            db_session.commit()
            flask.session['session_id'] = session.id
            return json_['email']
    return flask.abort(400, 'failed to validate')

if __name__ == '__main__':
    app.run(debug=True)
