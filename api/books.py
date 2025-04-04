from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from model.books import Book, ReadingProgress, ReadingGoal, BookClub, BookRecommendation
from model.user import User
from datetime import datetime, timedelta
from flask_cors import cross_origin

books_api = Blueprint('books_api', __name__)

@books_api.route('/api/books/currently-reading', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True, allow_headers=['*'], expose_headers=['*'])
@login_required
def get_currently_reading():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        return response, 200
        
    """Get the book the user is currently reading"""
    progress = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(ReadingProgress.last_updated.desc()).first()
    
    if not progress:
        return jsonify({"message": "No book currently being read"}), 404
    
    book = Book.query.get(progress.book_id)
    response = jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "progress": progress.progress_percentage,
        "current_page": progress.current_page,
        "total_pages": book.total_pages
    })
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    return response

@books_api.route('/api/books/stats', methods=['GET'])
@login_required
def get_reading_stats():
    """Get user's reading statistics"""
    # Get books read count
    books_read = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).count()
    
    # Calculate reading streak
    streak = 0
    today = datetime.now().date()
    current_date = today
    while True:
        has_read = ReadingProgress.query.filter(
            ReadingProgress.user_id == current_user.id,
            ReadingProgress.last_updated >= current_date,
            ReadingProgress.last_updated < current_date + timedelta(days=1)
        ).first()
        if not has_read:
            break
        streak += 1
        current_date -= timedelta(days=1)
    
    # Get reading hours (simplified for now)
    reading_hours = books_read * 5  # Assuming 5 hours per book
    
    # Get books in progress
    books_in_progress = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).count()
    
    return jsonify({
        "booksRead": books_read,
        "readingStreak": streak,
        "readingHours": reading_hours,
        "booksInProgress": books_in_progress
    })

@books_api.route('/api/books/goals', methods=['GET'])
@login_required
def get_reading_goals():
    """Get user's reading goals"""
    goal = ReadingGoal.query.filter_by(user_id=current_user.id).first()
    if not goal:
        return jsonify({
            "yearly_goal": 12,
            "daily_goal": 30,
            "books_read": 0,
            "minutes_read": 0
        })
    
    return jsonify({
        "yearly_goal": goal.yearly_goal,
        "daily_goal": goal.daily_goal,
        "books_read": goal.books_read,
        "minutes_read": goal.minutes_read
    })

@books_api.route('/api/books/recommendations', methods=['GET'])
@login_required
def get_book_recommendations():
    """Get personalized book recommendations"""
    recommendations = BookRecommendation.query.filter_by(
        user_id=current_user.id
    ).limit(5).all()
    
    return jsonify([{
        "id": rec.book.id,
        "title": rec.book.title,
        "author": rec.book.author,
        "cover_url": rec.book.cover_url
    } for rec in recommendations])

@books_api.route('/api/books/history', methods=['GET'])
@login_required
def get_reading_history():
    """Get user's reading history"""
    history = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(ReadingProgress.completion_date.desc()).limit(10).all()
    
    return jsonify([{
        "id": progress.book.id,
        "title": progress.book.title,
        "author": progress.book.author,
        "completionDate": progress.completion_date.isoformat(),
        "cover_url": progress.book.cover_url
    } for progress in history])

@books_api.route('/api/books/clubs', methods=['GET'])
@login_required
def get_book_clubs():
    """Get available book clubs"""
    clubs = BookClub.query.all()
    
    return jsonify([{
        "id": club.id,
        "name": club.name,
        "currentBook": club.current_book.title if club.current_book else "No book selected",
        "members": club.members.count()
    } for club in clubs])

@books_api.route('/api/books/progress', methods=['POST'])
@login_required
def update_reading_progress():
    """Update reading progress for a book"""
    data = request.get_json()
    book_id = data.get('bookId')
    progress = data.get('progress')
    
    if not book_id or not progress:
        return jsonify({"error": "Missing required fields"}), 400
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    reading_progress = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
        completed=False
    ).first()
    
    if not reading_progress:
        reading_progress = ReadingProgress(
            user_id=current_user.id,
            book_id=book_id,
            current_page=progress,
            total_pages=book.total_pages
        )
        db.session.add(reading_progress)
    else:
        reading_progress.current_page = progress
        reading_progress.last_updated = datetime.now()
        
        # Check if book is completed
        if progress >= book.total_pages:
            reading_progress.completed = True
            reading_progress.completion_date = datetime.now()
            
            # Update reading goals
            goal = ReadingGoal.query.filter_by(user_id=current_user.id).first()
            if goal:
                goal.books_read += 1
    
    db.session.commit()
    
    return jsonify({
        "message": "Progress updated successfully",
        "progress": reading_progress.progress_percentage
    }) 