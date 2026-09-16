from datetime import datetime
from Python_Project import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(130), unique=True, nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default="default.png")
    bio = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self):
        s=Serializer(app.config['SECRET_KEY'], salt='pw-reset')
        return s.dumps({'user_id':self.id})

    @staticmethod
    def verify_reset_token(token, age=3600):
        s= Serializer(app.config['SECRET_KEY'], salt='pw-reset')
        try:
            user_id  = s.loads(token, max_age=age)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}', '{self.username}', '{self.email}', '{self.image_file}')"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(50), nullable=False, default='default_icon.jpg')

    def __repr__(self):
        return f"Course('{self.title}')"