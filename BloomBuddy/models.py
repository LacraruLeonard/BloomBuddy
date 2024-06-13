from BloomBuddy import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
from sqlalchemy import Table, Column, Integer, ForeignKey


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    profile_image = db.Column(db.String(64), nullable=False, default='default_profile.png')
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('BlogPost', backref='author', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Username {self.username}"


class BlogPost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    title = db.Column(db.String(140), nullable=False)
    text = db.Column(db.Text, nullable=False)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __init__(self, title, text, user_id):
        self.title = title
        self.text = text
        self.user_id = user_id

    def __repr__(self):
        return f"Post ID: {self.id} -- Date: {self.date} -- {self.title}"


comments_replies = Table('comments_replies', db.Model.metadata,
                         Column('comment_id', Integer, ForeignKey('comment.id')),
                         Column('reply_id', Integer, ForeignKey('comment.id'))
                         )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='comments')
    post_id = db.Column(db.Integer, db.ForeignKey('blogpost.id'))
    replies = db.relationship('Comment', secondary=comments_replies, primaryjoin=id == comments_replies.c.comment_id,
                              secondaryjoin=id == comments_replies.c.reply_id, backref='parent_comments')

    def __repr__(self):
        return f'<Comment {self.text}>'


class Plant(db.Model):
    __tablename__ = 'plants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    age = db.Column(db.String(64), nullable=False)
    health = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, name, age, health, user_id):
        self.name = name
        self.age = age
        self.health = health
        self.user_id = user_id

    def __repr__(self):
        return f"Plant {self.name}, Age {self.age}, Health {self.health}"
