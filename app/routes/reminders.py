"""Reminder management routes."""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from app.models import Reminder, ReminderSchedule
from app.services.reminder_service import ReminderService
from app.middleware.auth import admin_required
from app.utils.decorators import paginated
from app.utils.helpers import paginate_query
from app import db

bp = Blueprint('reminders', __name__, url_prefix='/api/reminders')


@bp.route('', methods=['GET'])
@admin_required
@paginated(default_per_page=50, max_per_page=200)
def list_reminders(user, page, per_page):
    """List all reminders with filters."""
    query = Reminder.query
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # Filter by date
    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(Reminder.order_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    
    # Order by created date
    query = query.order_by(Reminder.created_at.desc())
    
    # Paginate
    result = paginate_query(query, page=page, per_page=per_page)
    
    return jsonify({
        'reminders': [r.to_dict() for r in result['items']],
        'pagination': {
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages']
        }
    }), 200


@bp.route('/send', methods=['POST'])
@admin_required
def send_reminders_manually(user):
    """Manually trigger reminders for a specific date."""
    try:
        target_date = request.json.get('date')
        if not target_date:
            # Default to tomorrow
            target_date = (date.today() + timedelta(days=1)).isoformat()
        
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        sent, failed = ReminderService.send_reminders_for_date(target_date_obj)
        
        return jsonify({
            'message': f'Reminders sent for {target_date}',
            'sent': sent,
            'failed': failed
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/schedules', methods=['GET'])
@admin_required
def list_schedules(user):
    """List all reminder schedules."""
    schedules = ReminderSchedule.query.order_by(ReminderSchedule.days_ahead).all()
    
    return jsonify({
        'schedules': [s.to_dict() for s in schedules]
    }), 200


@bp.route('/schedules', methods=['POST'])
@admin_required
def create_schedule(user):
    """Create a new reminder schedule."""
    try:
        data = request.json
        
        schedule = ReminderSchedule(
            name=data['name'],
            days_ahead=data['days_ahead'],
            reminder_time=datetime.strptime(data['reminder_time'], '%H:%M').time(),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule created successfully',
            'schedule': schedule.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@admin_required
def update_schedule(user, schedule_id):
    """Update a reminder schedule."""
    try:
        schedule = db.session.get(ReminderSchedule, schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        data = request.json
        
        if 'name' in data:
            schedule.name = data['name']
        if 'days_ahead' in data:
            schedule.days_ahead = data['days_ahead']
        if 'reminder_time' in data:
            schedule.reminder_time = datetime.strptime(data['reminder_time'], '%H:%M').time()
        if 'is_active' in data:
            schedule.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule updated successfully',
            'schedule': schedule.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@admin_required
def delete_schedule(user, schedule_id):
    """Delete a reminder schedule."""
    schedule = db.session.get(ReminderSchedule, schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'message': 'Schedule deleted successfully'}), 200
