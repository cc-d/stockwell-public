import sqlite3
import os
from main import db, root_path, json_data

# remove error with previous table being defined in the metadata
db.metadata.clear()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    logged_in = db.Column(db.Boolean, default=False, nullable=False)

    def get_words(self):
        return db.session.query(Word).filter_by(reviewer='username').all()

    def log_in_out(self, set_status=None):
        # sets status to logged out if logged in, and vice versa
        if set_status:
            self.logged_in = set_status
        else:
            if self.logged_in is False:
                self.logged_in = True
            else:
                self.logged_in = False

        # ensure any words this user is processing become freely avaliable
        if self.logged_in is False:
            words = db.session.query(Word)\
                                .filter_by(reviewer=self.username)\
                                .filter_by(status='reviewing').delete()

        db.session.add(self)
        db.session.commit()

        return self


    def __repr__(self): 
        return '<User %r>' % self.username

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), unique=True, nullable=False)
    reviewer = db.Column(db.String(255), db.ForeignKey('user.username'))
    status = db.Column(db.String(255), default='reviewing', nullable=False)

    def get_reviewer(self):
        return db.session.query(User).filter_by(username=self.reviewer).first()

class GoogleImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), db.ForeignKey('word.text'))
    url = db.Column(db.String(255), nullable=True, default=None)

def create_new_db():
    try:
        os.remove(root_path + '/sqlite.db')
    except FileNotFoundError:
        # if the database doesn't exist already ignore the error
        pass
    db.create_all()

if __name__ == '__main__':
    create_new_db()