from __init__ import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    total_pages = db.Column(db.Integer, nullable=False)
    cover_url = db.Column(db.String(255))
    genre = db.Column(db.String(100))
    published_date = db.Column(db.Date)
    
    def __init__(self, title, author, total_pages, cover_url=None, genre=None, published_date=None):
        self.title = title
        self.author = author
        self.total_pages = total_pages
        self.cover_url = cover_url
        self.genre = genre
        self.published_date = published_date
    
    def read(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "total_pages": self.total_pages,
            "cover_url": self.cover_url,
            "genre": self.genre,
            "published_date": self.published_date.isoformat() if self.published_date else None
        }

class ReadingProgress(db.Model):
    __tablename__ = 'reading_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    current_page = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.now)
    completion_date = db.Column(db.DateTime)
    
    book = db.relationship('Book', backref='reading_progress')
    user = db.relationship('User', backref='reading_progress')
    
    @property
    def progress_percentage(self):
        if not self.book:
            return 0
        return int((self.current_page / self.book.total_pages) * 100)
    
    def __init__(self, user_id, book_id, current_page=0, completed=False):
        self.user_id = user_id
        self.book_id = book_id
        self.current_page = current_page
        self.completed = completed
        self.last_updated = datetime.now()
    
    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "current_page": self.current_page,
            "completed": self.completed,
            "progress_percentage": self.progress_percentage,
            "last_updated": self.last_updated.isoformat(),
            "completion_date": self.completion_date.isoformat() if self.completion_date else None
        }

class ReadingGoal(db.Model):
    __tablename__ = 'reading_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    yearly_goal = db.Column(db.Integer, default=12)
    daily_goal = db.Column(db.Integer, default=30)  # minutes
    books_read = db.Column(db.Integer, default=0)
    minutes_read = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref='reading_goals')
    
    def __init__(self, user_id, yearly_goal=12, daily_goal=30):
        self.user_id = user_id
        self.yearly_goal = yearly_goal
        self.daily_goal = daily_goal
        self.books_read = 0
        self.minutes_read = 0
    
    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "yearly_goal": self.yearly_goal,
            "daily_goal": self.daily_goal,
            "books_read": self.books_read,
            "minutes_read": self.minutes_read
        }

class BookClub(db.Model):
    __tablename__ = 'book_clubs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    current_book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    current_book = db.relationship('Book', backref='book_clubs')
    members = db.relationship('User', secondary='book_club_members', backref='book_clubs')
    
    def __init__(self, name, description=None, current_book_id=None):
        self.name = name
        self.description = description
        self.current_book_id = current_book_id
    
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "current_book_id": self.current_book_id,
            "members_count": len(self.members),
            "created_at": self.created_at.isoformat()
        }

class BookRecommendation(db.Model):
    __tablename__ = 'book_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    book = db.relationship('Book', backref='recommendations')
    user = db.relationship('User', backref='book_recommendations')
    
    def __init__(self, user_id, book_id, score=None):
        self.user_id = user_id
        self.book_id = book_id
        self.score = score
    
    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "score": self.score,
            "created_at": self.created_at.isoformat()
        }

# Association table for book club members
book_club_members = db.Table('book_club_members',
    db.Column('club_id', db.Integer, db.ForeignKey('book_clubs.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
) 