from sqlite3 import IntegrityError
from sqlalchemy import Text
from __init__ import app, db
from model.user import User
from model.group import Group
from datetime import datetime

class CarComment(db.Model):

    __tablename__ = "carcomments" 
     id = db.Column(db.Integer, primary_key=True)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _postid = db.column(db.Integer, db.ForeignKey("carPosts.id"), nullable=False)
    _content = db.column(db.String(255), nullable=False)

    def __init__(self, uid, postid, content):
        self._uid = uid 
        self._postid = postid
        self._content = content