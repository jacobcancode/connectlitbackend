from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from model.reading import ReadingJournal
from model.books import Book
from __init__ import db
from datetime import datetime
from sqlalchemy import distinct
from flask_cors import cross_origin
import logging

journal_bp = Blueprint('journal', __name__)

def handle_options():
    """Handle OPTIONS requests for CORS preflight"""
    return jsonify({}), 200

@journal_bp.route('/api/reading/journal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def create_journal_entry():
    if request.method == 'OPTIONS':
        return handle_options()
        
    try:
        data = request.get_json()
        current_app.logger.info(f'Received data: {data}')
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['book_id', 'page_number', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            current_app.logger.error(f'Missing fields: {missing_fields}')
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Validate book_id
        if not data['book_id'] or data['book_id'] == 'undefined':
            return jsonify({'error': 'Invalid book_id'}), 400
            
        book = Book.query.filter_by(id=data['book_id']).first()
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        # Create new journal entry
        entry = ReadingJournal(
            user_id=current_user.id,
            book_id=data['book_id'],
            page_number=data['page_number'],
            content=data['content']
        )
        
        entry.create()
        return jsonify(entry.read()), 201
    except Exception as e:
        current_app.logger.error(f'Error creating journal entry: {str(e)}')
        return jsonify({'error': 'Failed to create journal entry'}), 500

@journal_bp.route('/api/reading/journal/<book_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def get_journal_entries(book_id):
    if request.method == 'OPTIONS':
        return handle_options()
        
    try:
        # Handle undefined book_id
        if not book_id or book_id == 'undefined':
            return jsonify({'error': 'Invalid book_id'}), 400
            
        # Validate book_id
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        # Get all journal entries for the current user and specific book
        entries = ReadingJournal.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).order_by(ReadingJournal._created_at.desc()).all()
        
        return jsonify([entry.read() for entry in entries]), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching journal entries: {str(e)}')
        return jsonify({'error': 'Failed to fetch journal entries'}), 500

@journal_bp.route('/api/reading/journal/<int:entry_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def update_journal_entry(entry_id):
    if request.method == 'OPTIONS':
        return handle_options()
        
    try:
        entry = ReadingJournal.query.filter_by(id=entry_id, user_id=current_user.id).first()
        if not entry:
            return jsonify({'error': 'Journal entry not found'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        update_data = {}
        if 'page_number' in data:
            update_data['page_number'] = data['page_number']
        if 'content' in data:
            update_data['content'] = data['content']
            
        if update_data:
            entry.update(**update_data)
        
        return jsonify(entry.read()), 200
    except Exception as e:
        current_app.logger.error(f'Error updating journal entry: {str(e)}')
        return jsonify({'error': 'Failed to update journal entry'}), 500

@journal_bp.route('/api/reading/journal/<int:entry_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def delete_journal_entry(entry_id):
    if request.method == 'OPTIONS':
        return handle_options()
        
    try:
        entry = ReadingJournal.query.filter_by(id=entry_id, user_id=current_user.id).first()
        if not entry:
            return jsonify({'error': 'Journal entry not found'}), 404
            
        entry.delete()
        return jsonify({'message': 'Journal entry deleted successfully'}), 200
    except Exception as e:
        current_app.logger.error(f'Error deleting journal entry: {str(e)}')
        return jsonify({'error': 'Failed to delete journal entry'}), 500

@journal_bp.route('/api/reading/journal/books', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def get_journal_books():
    if request.method == 'OPTIONS':
        return handle_options()
        
    try:
        # Get all unique books that have journal entries for the current user
        books = db.session.query(distinct(ReadingJournal._book_id)).filter_by(
            user_id=current_user.id
        ).all()
        
        # Get book details for each book_id
        book_details = []
        for book_id in books:
            book = Book.query.filter_by(id=book_id[0]).first()
            if book:
                book_details.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'cover': book.cover_url
                })
        
        return jsonify(book_details), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching journal books: {str(e)}')
        return jsonify({'error': 'Failed to fetch journal books'}), 500 