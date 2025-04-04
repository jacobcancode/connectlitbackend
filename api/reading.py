from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from model.reading import ReadingSession, ReadingSpeed
from model.books import Book
from __init__ import db

reading_bp = Blueprint('reading', __name__)

@reading_bp.route('/sessions', methods=['POST'])
@login_required
def start_reading_session():
    data = request.get_json()
    book_id = data.get('book_id')
    
    if book_id:
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
    
    session = ReadingSession(current_user.id, book_id)
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.read()), 201

@reading_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@login_required
def end_reading_session(session_id):
    session = ReadingSession.query.get_or_404(session_id)
    
    if session.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    session.end_session()
    db.session.commit()
    
    return jsonify(session.read())

@reading_bp.route('/sessions', methods=['GET'])
@login_required
def get_reading_sessions():
    sessions = ReadingSession.query.filter_by(user_id=current_user.id).all()
    return jsonify([session.read() for session in sessions])

@reading_bp.route('/speed', methods=['POST'])
@login_required
def record_reading_speed():
    data = request.get_json()
    words_per_minute = data.get('words_per_minute')
    words_read = data.get('words_read')
    minutes_taken = data.get('minutes_taken')
    
    if not all([words_per_minute, words_read, minutes_taken]):
        return jsonify({"error": "Missing required fields"}), 400
    
    speed = ReadingSpeed(
        user_id=current_user.id,
        words_per_minute=words_per_minute,
        words_read=words_read,
        minutes_taken=minutes_taken
    )
    
    db.session.add(speed)
    db.session.commit()
    
    return jsonify(speed.read()), 201

@reading_bp.route('/speed', methods=['GET'])
@login_required
def get_reading_speeds():
    speeds = ReadingSpeed.query.filter_by(user_id=current_user.id).all()
    return jsonify([speed.read() for speed in speeds]) 