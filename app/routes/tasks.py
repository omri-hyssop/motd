"""Task trigger routes (intended for Cloud Scheduler / cron execution)."""
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request

from app.tasks.order_tasks import send_restaurant_summaries
from app.tasks.reminder_tasks import cleanup_old_sessions, send_daily_reminders

bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


def _require_task_token():
    token = current_app.config.get('TASK_TRIGGER_TOKEN')
    if not token:
        return jsonify({'error': 'Not found'}), 404
    provided = request.headers.get('X-Task-Token')
    if not provided or provided != token:
        return jsonify({'error': 'Unauthorized'}), 401
    return None


@bp.route('/run', methods=['POST'])
def run_task():
    """Run a background task on-demand.

    Request JSON:
      - task: daily_reminders | restaurant_summaries | cleanup_old_sessions
    """
    auth_err = _require_task_token()
    if auth_err:
        return auth_err

    payload = request.get_json(silent=True) or {}
    task = payload.get('task')
    app = current_app._get_current_object()

    started_at = datetime.utcnow().isoformat() + 'Z'

    if task == 'daily_reminders':
        send_daily_reminders(app)
    elif task == 'restaurant_summaries':
        send_restaurant_summaries(app)
    elif task == 'cleanup_old_sessions':
        cleanup_old_sessions(app)
    else:
        return jsonify({'error': 'Unknown task'}), 400

    return jsonify({'ok': True, 'task': task, 'started_at': started_at}), 200
