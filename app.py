"""
Personal Dashboard - Flask Application
A modern, self-contained dashboard with weather, to-do list, notes, calendar,
pomodoro timer, and productivity tracking.
"""
from flask import Flask, render_template, jsonify, request, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime, timedelta
import random
import calendar
import csv
import io

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)


# ============================================
# Database Models
# ============================================

class Todo(db.Model):
    """To-do item model."""
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Note(db.Model):
    """Notes/Journal model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    color = db.Column(db.String(20), default='primary')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Event(db.Model):
    """Calendar event model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10))
    color = db.Column(db.String(20), default='primary')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time,
            'color': self.color
        }


class PomodoroSession(db.Model):
    """Pomodoro session tracking."""
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer, default=25)  # minutes
    completed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'duration': self.duration,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ScheduleItem(db.Model):
    """Schedule item model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(500))
    color = db.Column(db.String(20), default='primary')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'time': self.time,
            'description': self.description,
            'color': self.color
        }


# ============================================
# Sample Data
# ============================================

MOTIVATIONAL_QUOTES = [
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"quote": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
    {"quote": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"quote": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
    {"quote": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
    {"quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"quote": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"},
    {"quote": "Your limitation—it's only your imagination.", "author": "Unknown"},
    {"quote": "Push yourself, because no one else is going to do it for you.", "author": "Unknown"},
    {"quote": "Great things never come from comfort zones.", "author": "Unknown"},
    {"quote": "Dream it. Wish it. Do it.", "author": "Unknown"},
    {"quote": "Success doesn't just find you. You have to go out and get it.", "author": "Unknown"},
    {"quote": "The harder you work for something, the greater you'll feel when you achieve it.", "author": "Unknown"},
    {"quote": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"quote": "Everything you've ever wanted is on the other side of fear.", "author": "George Addair"},
    {"quote": "Hardships often prepare ordinary people for an extraordinary destiny.", "author": "C.S. Lewis"},
]

# Mock weather data (no API required)
def get_mock_weather():
    """Generate mock weather data - no external API needed."""
    conditions = [
        {"condition": "Sunny", "icon": "sun", "temp_range": (22, 32)},
        {"condition": "Partly Cloudy", "icon": "cloud-sun", "temp_range": (20, 28)},
        {"condition": "Cloudy", "icon": "cloud", "temp_range": (18, 25)},
        {"condition": "Light Rain", "icon": "cloud-rain", "temp_range": (16, 22)},
        {"condition": "Clear", "icon": "moon-stars", "temp_range": (18, 26)},
    ]
    
    # Use day of month to get consistent weather per day
    day_index = datetime.now().day % len(conditions)
    weather = conditions[day_index]
    
    temp_min, temp_max = weather["temp_range"]
    hour = datetime.now().hour
    # Temperature varies by time of day
    temp = temp_min + (temp_max - temp_min) * (0.5 + 0.5 * (1 - abs(14 - hour) / 14))
    
    # Generate 5-day forecast
    forecast = []
    for i in range(5):
        day_condition = conditions[(day_index + i) % len(conditions)]
        forecast.append({
            "day": (datetime.now() + timedelta(days=i)).strftime("%a"),
            "high": day_condition["temp_range"][1] + random.randint(-2, 2),
            "low": day_condition["temp_range"][0] + random.randint(-2, 2),
            "icon": day_condition["icon"]
        })
    
    return {
        "location": "Shenzhen, China",
        "temperature": round(temp),
        "condition": weather["condition"],
        "icon": weather["icon"],
        "humidity": 50 + random.randint(0, 30),
        "wind": 5 + random.randint(0, 15),
        "forecast": forecast
    }


def init_sample_data():
    """Initialize database with sample data."""
    if Todo.query.count() == 0:
        sample_todos = [
            Todo(task="Complete MIS2001 assignment", completed=False),
            Todo(task="Review Flask documentation", completed=True),
            Todo(task="Build dashboard project", completed=True),
            Todo(task="Practice Python coding", completed=False),
            Todo(task="Prepare for midterm exam", completed=False),
        ]
        db.session.add_all(sample_todos)
    
    if ScheduleItem.query.count() == 0:
        sample_schedule = [
            ScheduleItem(title="Morning Standup", time="09:00", description="Daily team sync", color="primary"),
            ScheduleItem(title="MIS2001 Lecture", time="10:30", description="Chapter 5: Database Design", color="success"),
            ScheduleItem(title="Lunch Break", time="12:00", description="", color="warning"),
            ScheduleItem(title="Project Work", time="13:00", description="Work on Flask dashboard", color="info"),
            ScheduleItem(title="Study Session", time="15:30", description="Review notes and practice", color="secondary"),
            ScheduleItem(title="Gym", time="17:00", description="Cardio and weights", color="danger"),
        ]
        db.session.add_all(sample_schedule)
    
    if Note.query.count() == 0:
        sample_notes = [
            Note(title="Flask Tips", content="Remember to use blueprints for larger applications. Keep routes organized!", color="primary"),
            Note(title="Meeting Notes", content="Discussed project timeline. Deadline is next Friday. Need to complete API integration.", color="success"),
            Note(title="Ideas", content="- Add dark mode\n- Mobile responsive design\n- Pomodoro timer\n- Calendar integration", color="warning"),
        ]
        db.session.add_all(sample_notes)
    
    if Event.query.count() == 0:
        today = datetime.now().date()
        sample_events = [
            Event(title="Team Meeting", date=today, time="10:00", description="Weekly sync", color="primary"),
            Event(title="Project Deadline", date=today + timedelta(days=3), time="23:59", description="Submit final project", color="danger"),
            Event(title="Study Group", date=today + timedelta(days=1), time="14:00", description="Library room 201", color="success"),
            Event(title="Doctor Appointment", date=today + timedelta(days=5), time="09:30", color="warning"),
        ]
        db.session.add_all(sample_events)
    
    db.session.commit()


# ============================================
# Page Routes
# ============================================

@app.route('/')
def dashboard():
    """Main dashboard page."""
    todos = Todo.query.order_by(Todo.created_at.desc()).limit(5).all()
    schedule = ScheduleItem.query.order_by(ScheduleItem.time).all()
    notes = Note.query.order_by(Note.updated_at.desc()).limit(3).all()
    quote = random.choice(MOTIVATIONAL_QUOTES)
    weather = get_mock_weather()
    
    # Productivity stats
    total_todos = Todo.query.count()
    completed_todos = Todo.query.filter_by(completed=True).count()
    today_sessions = PomodoroSession.query.filter(
        PomodoroSession.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
    ).count()
    
    # Weekly productivity data for chart
    weekly_data = []
    for i in range(7):
        day = datetime.now() - timedelta(days=6-i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        sessions = PomodoroSession.query.filter(
            PomodoroSession.created_at >= day_start,
            PomodoroSession.created_at < day_end
        ).count()
        weekly_data.append({
            'day': day.strftime('%a'),
            'sessions': sessions
        })
    
    return render_template('dashboard.html',
                         todos=todos,
                         schedule=schedule,
                         notes=notes,
                         quote=quote,
                         weather=weather,
                         total_todos=total_todos,
                         completed_todos=completed_todos,
                         today_sessions=today_sessions,
                         weekly_data=weekly_data,
                         current_date=datetime.now())


@app.route('/calendar')
def calendar_page():
    """Calendar page."""
    # Get current month/year from query params or use current date
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Handle month overflow
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1
    
    # Get calendar data
    cal = calendar.Calendar(firstweekday=6)  # Start on Sunday
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get events for this month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    events = Event.query.filter(
        Event.date >= first_day,
        Event.date <= last_day
    ).order_by(Event.date, Event.time).all()
    
    # Group events by date
    events_by_date = {}
    for event in events:
        date_str = event.date.isoformat()
        if date_str not in events_by_date:
            events_by_date[date_str] = []
        events_by_date[date_str].append(event.to_dict())
    
    return render_template('calendar.html',
                         year=year,
                         month=month,
                         month_name=month_name,
                         month_days=month_days,
                         events_by_date=events_by_date,
                         today=datetime.now().date())


@app.route('/pomodoro')
def pomodoro():
    """Pomodoro timer page."""
    # Get today's sessions
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = PomodoroSession.query.filter(
        PomodoroSession.created_at >= today_start
    ).count()
    
    # Get total sessions
    total_sessions = PomodoroSession.query.count()
    
    # Calculate total focus time
    total_minutes = db.session.query(db.func.sum(PomodoroSession.duration)).scalar() or 0
    total_hours = total_minutes // 60
    
    return render_template('pomodoro.html',
                         today_sessions=today_sessions,
                         total_sessions=total_sessions,
                         total_hours=total_hours)


@app.route('/notes')
def notes_page():
    """Notes page."""
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return render_template('notes.html', notes=notes)


@app.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')


# ============================================
# API Routes - Todos
# ============================================

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos."""
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([todo.to_dict() for todo in todos])


@app.route('/api/todos', methods=['POST'])
def add_todo():
    """Add a new todo."""
    data = request.get_json()
    todo = Todo(task=data.get('task', ''))
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Toggle todo completion status."""
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    if 'completed' in data:
        todo.completed = data['completed']
    if 'task' in data:
        todo.task = data['task']
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo."""
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted'})


# ============================================
# API Routes - Notes
# ============================================

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all notes."""
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])


@app.route('/api/notes', methods=['POST'])
def add_note():
    """Add a new note."""
    data = request.get_json()
    note = Note(
        title=data.get('title', 'Untitled'),
        content=data.get('content', ''),
        color=data.get('color', 'primary')
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a single note."""
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note."""
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']
    if 'color' in data:
        note.color = data['color']
    note.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(note.to_dict())


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note."""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted'})


# ============================================
# API Routes - Events
# ============================================

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events or filter by date range."""
    start = request.args.get('start')
    end = request.args.get('end')
    
    query = Event.query
    if start:
        query = query.filter(Event.date >= start)
    if end:
        query = query.filter(Event.date <= end)
    
    events = query.order_by(Event.date, Event.time).all()
    return jsonify([event.to_dict() for event in events])


@app.route('/api/events', methods=['POST'])
def add_event():
    """Add a new event."""
    data = request.get_json()
    event = Event(
        title=data.get('title', 'Untitled'),
        description=data.get('description', ''),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        time=data.get('time', ''),
        color=data.get('color', 'primary')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a single event."""
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())


@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an event."""
    event = Event.query.get_or_404(event_id)
    data = request.get_json()
    if 'title' in data:
        event.title = data['title']
    if 'description' in data:
        event.description = data['description']
    if 'date' in data:
        event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if 'time' in data:
        event.time = data['time']
    if 'color' in data:
        event.color = data['color']
    db.session.commit()
    return jsonify(event.to_dict())


@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event."""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'})


# ============================================
# API Routes - Pomodoro
# ============================================

@app.route('/api/pomodoro/complete', methods=['POST'])
def complete_pomodoro():
    """Record a completed pomodoro session."""
    data = request.get_json()
    session = PomodoroSession(
        duration=data.get('duration', 25),
        completed=True
    )
    db.session.add(session)
    db.session.commit()
    return jsonify(session.to_dict()), 201


@app.route('/api/pomodoro/stats', methods=['GET'])
def get_pomodoro_stats():
    """Get pomodoro statistics."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_sessions = PomodoroSession.query.filter(
        PomodoroSession.created_at >= today_start
    ).count()
    
    total_sessions = PomodoroSession.query.count()
    total_minutes = db.session.query(db.func.sum(PomodoroSession.duration)).scalar() or 0
    
    return jsonify({
        'today_sessions': today_sessions,
        'total_sessions': total_sessions,
        'total_hours': total_minutes // 60
    })


# ============================================
# API Routes - Other
# ============================================

@app.route('/api/quote')
def get_quote():
    """Get a random motivational quote."""
    return jsonify(random.choice(MOTIVATIONAL_QUOTES))


@app.route('/api/weather')
def get_weather():
    """Get mock weather data."""
    return jsonify(get_mock_weather())


@app.route('/api/schedule')
def get_schedule():
    """Get schedule items."""
    items = ScheduleItem.query.order_by(ScheduleItem.time).all()
    return jsonify([item.to_dict() for item in items])


@app.route('/api/health')
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Dashboard is running!',
        'timestamp': datetime.now().isoformat()
    })


# ============================================
# Export Routes
# ============================================

@app.route('/export/todos/csv')
def export_todos_csv():
    """Export todos to CSV file."""
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Task', 'Status', 'Created At'])
    for todo in todos:
        writer.writerow([
            todo.id,
            todo.task,
            'Completed' if todo.completed else 'Pending',
            todo.created_at.strftime('%Y-%m-%d %H:%M:%S') if todo.created_at else 'N/A'
        ])
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=todos_{datetime.now().strftime("%Y%m%d")}.csv'
    return response


@app.route('/export/notes/csv')
def export_notes_csv():
    """Export notes to CSV file."""
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Content', 'Color', 'Created At', 'Updated At'])
    for note in notes:
        writer.writerow([
            note.id,
            note.title,
            note.content.replace('\n', ' ').replace('\r', ' ') if note.content else '',
            note.color,
            note.created_at.strftime('%Y-%m-%d %H:%M:%S') if note.created_at else 'N/A',
            note.updated_at.strftime('%Y-%m-%d %H:%M:%S') if note.updated_at else 'N/A'
        ])
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=notes_{datetime.now().strftime("%Y%m%d")}.csv'
    return response


@app.route('/export/calendar/csv')
def export_calendar_csv():
    """Export calendar events to CSV file."""
    events = Event.query.order_by(Event.date, Event.time).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Description', 'Date', 'Time', 'Color'])
    for event in events:
        writer.writerow([
            event.id,
            event.title,
            event.description.replace('\n', ' ').replace('\r', ' ') if event.description else '',
            event.date.strftime('%Y-%m-%d') if event.date else 'N/A',
            event.time,
            event.color
        ])
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=events_{datetime.now().strftime("%Y%m%d")}.csv'
    return response


# ============================================
# Run Application
# ============================================

with app.app_context():
    db.create_all()
    init_sample_data()

if __name__ == '__main__':
    app.run(debug=True)
