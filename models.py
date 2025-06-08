from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """Management users who can access the system"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='manager')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, username=None, full_name=None, role='manager', **kwargs):
        super().__init__(**kwargs)
        if username:
            self.username = username
        if full_name:
            self.full_name = full_name
        self.role = role
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    """Student records with ID card information"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    card_id = db.Column(db.String(50), unique=True, nullable=False)  # Biometric card ID
    name = db.Column(db.String(120), nullable=False)
    session = db.Column(db.String(10), nullable=False)  # AN, FN
    campus = db.Column(db.String(10), nullable=False)   # AEC, ACET, ACOE
    course = db.Column(db.String(20), nullable=False)   # CE, EEE, ME, etc.
    year = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with attendance records
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    
    def __init__(self, roll_number=None, card_id=None, name=None, session=None, campus=None, course=None, year=1, **kwargs):
        super().__init__(**kwargs)
        if roll_number:
            self.roll_number = roll_number
        if card_id:
            self.card_id = card_id
        if name:
            self.name = name
        if session:
            self.session = session
        if campus:
            self.campus = campus
        if course:
            self.course = course
        self.year = year

class AttendanceRecord(db.Model):
    """Individual attendance records from biometric scans"""
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    card_id = db.Column(db.String(50), nullable=False)  # For direct lookup
    scan_datetime = db.Column(db.DateTime, nullable=False)
    scan_date = db.Column(db.Date, nullable=False)
    scan_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), default='Main Campus')
    scanner_id = db.Column(db.String(50))  # Which scanner recorded this
    status = db.Column(db.String(20), default='present')  # present, late, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one record per student per day
    __table_args__ = (db.UniqueConstraint('student_id', 'scan_date', name='unique_student_daily_attendance'),)
    
    def __init__(self, student_id=None, card_id=None, scan_datetime=None, scan_date=None, scan_time=None, location='Main Campus', scanner_id=None, status='present', **kwargs):
        super().__init__(**kwargs)
        if student_id:
            self.student_id = student_id
        if card_id:
            self.card_id = card_id
        if scan_datetime:
            self.scan_datetime = scan_datetime
        if scan_date:
            self.scan_date = scan_date
        if scan_time:
            self.scan_time = scan_time
        self.location = location
        if scanner_id:
            self.scanner_id = scanner_id
        self.status = status

class AttendanceSession(db.Model):
    """Define attendance sessions for different time periods"""
    __tablename__ = 'attendance_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(50), nullable=False)  # Morning, Afternoon, etc.
    session_code = db.Column(db.String(10), nullable=False)  # AN, FN
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, session_name=None, session_code=None, start_time=None, end_time=None, **kwargs):
        super().__init__(**kwargs)
        if session_name:
            self.session_name = session_name
        if session_code:
            self.session_code = session_code
        if start_time:
            self.start_time = start_time
        if end_time:
            self.end_time = end_time
