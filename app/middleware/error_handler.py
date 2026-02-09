"""Global error handlers."""
from flask import jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register global error handlers."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Marshmallow validation errors."""
        return jsonify({
            'error': 'Validation error',
            'messages': error.messages
        }), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity errors."""
        app.logger.error(f'Integrity error: {str(error)}')
        
        # Check for specific constraint violations
        error_msg = str(error.orig)
        if 'uq_user_order_date' in error_msg or 'unique constraint' in error_msg.lower():
            return jsonify({
                'error': 'Duplicate order',
                'message': 'You already have an order for this date'
            }), 409
        elif 'foreign key' in error_msg.lower():
            return jsonify({
                'error': 'Invalid reference',
                'message': 'Referenced record does not exist'
            }), 400
        else:
            return jsonify({
                'error': 'Database error',
                'message': 'A database constraint was violated'
            }), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """Handle general database errors."""
        app.logger.error(f'Database error: {str(error)}')
        return jsonify({
            'error': 'Database error',
            'message': 'An error occurred while accessing the database'
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP exceptions."""
        return jsonify({
            'error': error.name,
            'message': error.description
        }), error.code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle 500 errors."""
        app.logger.error(f'Server error: {str(error)}')
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors."""
        app.logger.error(f'Unexpected error: {str(error)}', exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
