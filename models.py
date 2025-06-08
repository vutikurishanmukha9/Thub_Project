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
