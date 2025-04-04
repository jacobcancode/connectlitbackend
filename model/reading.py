from __init__ import db, app
from datetime import datetime

class ReadingSession(db.Model):
    __tablename__ = 'reading_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # Duration in seconds
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    
    user = db.relationship('User', backref='reading_sessions')
    book = db.relationship('Book', backref='reading_sessions')
    
    def __init__(self, user_id, book_id=None):
        self.user_id = user_id
        self.book_id = book_id
        self.start_time = datetime.now()
    
    def end_session(self):
        self.end_time = datetime.now()
        self.duration = int((self.end_time - self.start_time).total_seconds())
    
    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "book_id": self.book_id
        }

class ReadingSpeed(db.Model):
    __tablename__ = 'reading_speeds'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    words_per_minute = db.Column(db.Integer, nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.now)
    words_read = db.Column(db.Integer, nullable=False)
    minutes_taken = db.Column(db.Integer, nullable=False)
    
    user = db.relationship('User', backref='reading_speeds')
    
    def __init__(self, user_id, words_per_minute, words_read, minutes_taken):
        self.user_id = user_id
        self.words_per_minute = words_per_minute
        self.words_read = words_read
        self.minutes_taken = minutes_taken
    
    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "words_per_minute": self.words_per_minute,
            "test_date": self.test_date.isoformat(),
            "words_read": self.words_read,
            "minutes_taken": self.minutes_taken
        }

class ReadingJournal(db.Model):
    __tablename__ = 'reading_journals'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    _page_number = db.Column(db.Integer, nullable=False)
    _content = db.Column(db.Text, nullable=False)
    _created_at = db.Column(db.DateTime, default=datetime.utcnow)
    _updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('journal_entries', lazy=True))
    book = db.relationship('Book', backref=db.backref('journal_entries', lazy=True))

    def __init__(self, user_id, book_id, page_number, content):
        """
        Constructor for ReadingJournal.
        
        Args:
            user_id (int): The ID of the user creating the entry
            book_id (int): The ID of the book the entry is for
            page_number (int): The page number the entry is for
            content (str): The content of the journal entry
        """
        self._user_id = user_id
        self._book_id = book_id
        self._page_number = page_number
        self._content = content

    def create(self):
        """
        Create a new journal entry in the database.
        
        Raises:
            Exception: If there's an error creating the entry
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        """
        Read the journal entry data.
        
        Returns:
            dict: A dictionary containing the journal entry data
        """
        return {
            'id': self.id,
            'book_id': self._book_id,
            'page_number': self._page_number,
            'content': self._content,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat(),
            'book': {
                'title': self.book.title,
                'author': self.book.author,
                'cover': self.book.cover_url
            }
        }

    def update(self, **kwargs):
        """
        Update the journal entry with new data.
        
        Args:
            **kwargs: Key-value pairs of fields to update
            
        Raises:
            Exception: If there's an error updating the entry
        """
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}") and value is not None:
                setattr(self, f"_{key}", value)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """
        Delete the journal entry from the database.
        
        Raises:
            Exception: If there's an error deleting the entry
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

def initJournal():
    """Initialize the journal table in the database."""
    try:
        # Check if there are any existing journal entries
        if ReadingJournal.query.first() is None:
            print("No existing journal entries found.")
        else:
            print("Journal entries already exist in the database.")
    except Exception as e:
        print(f"Error initializing journal table: {str(e)}")
        db.session.rollback() 