import logging
from datetime import datetime, date, time
from flask import render_template, request, jsonify, session, redirect, url_for, make_response
from app import app, db
from models import User, Student, AttendanceRecord, AttendanceSession
from utils import generate_excel_report, validate_biometric_data
import json

def create_default_data():
    """Create default users and sample data if they don't exist"""
    try:
        # Create default admin user
        if not User.query.filter_by(username='Shanmukh').first():
            admin = User(username='Shanmukh', full_name='Shanmukh Admin', role='admin')
            admin.set_password('1234')
            db.session.add(admin)
            
        # Create default attendance sessions
        if not AttendanceSession.query.first():
            morning_session = AttendanceSession(
                session_name='Morning Session',
                session_code='AN',
                start_time=time(9, 0),
                end_time=time(12, 0)
            )
            afternoon_session = AttendanceSession(
                session_name='Afternoon Session', 
                session_code='FN',
                start_time=time(13, 0),
                end_time=time(17, 0)
            )
            db.session.add(morning_session)
            db.session.add(afternoon_session)
            
        # Create sample students
        if not Student.query.first():
            students = [
                Student(roll_number='001', card_id='CARD001', name='John Doe', 
                       session='AN', campus='AEC', course='CE'),
                Student(roll_number='002', card_id='CARD002', name='Jane Smith',
                       session='AN', campus='AEC', course='EEE'),
                Student(roll_number='003', card_id='CARD003', name='Alice Johnson',
                       session='FN', campus='ACET', course='CSE'),
                Student(roll_number='004', card_id='CARD004', name='Bob Wilson',
                       session='AN', campus='ACOE', course='ME'),
                Student(roll_number='005', card_id='CARD005', name='Carol Brown',
                       session='FN', campus='AEC', course='ECE'),
            ]
            for student in students:
                db.session.add(student)
                
        db.session.commit()
        logging.info("Default data created successfully")
    except Exception as e:
        logging.error(f"Error creating default data: {e}")
        db.session.rollback()

@app.route('/')
def index():
    """Main page - login if not authenticated, dashboard if authenticated"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login authentication"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'})
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            logging.info(f"User {username} logged in successfully")
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            logging.warning(f"Failed login attempt for username: {username}")
            return jsonify({'success': False, 'message': 'Invalid username or password'})
            
    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed'})

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        logging.info(f"User {username} logged out")
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        logging.error(f"Logout error: {e}")
        return jsonify({'success': False, 'message': 'Logout failed'})

@app.route('/api/biometric/scan', methods=['POST'])
def biometric_scan():
    """API endpoint to receive attendance data from biometric scanners"""
    try:
        data = request.get_json()
        
        if not validate_biometric_data(data):
            return jsonify({'success': False, 'message': 'Invalid biometric data format'})
        
        card_id = data.get('card_id')
        scan_datetime_str = data.get('timestamp')
        scanner_id = data.get('scanner_id', 'unknown')
        location = data.get('location', 'Main Campus')
        
        # Parse timestamp
        scan_datetime = datetime.fromisoformat(scan_datetime_str.replace('Z', '+00:00'))
        scan_date = scan_datetime.date()
        scan_time = scan_datetime.time()
        
        # Find student by card ID
        student = Student.query.filter_by(card_id=card_id, is_active=True).first()
        if not student:
            logging.warning(f"Unknown card ID scanned: {card_id}")
            return jsonify({'success': False, 'message': 'Student not found'})
        
        # Check if attendance already recorded for today
        existing_record = AttendanceRecord.query.filter_by(
            student_id=student.id, 
            scan_date=scan_date
        ).first()
        
        if existing_record:
            logging.info(f"Duplicate scan attempt for student {student.roll_number} on {scan_date}")
            return jsonify({
                'success': True, 
                'message': 'Attendance already recorded', 
                'duplicate': True,
                'student_name': student.name,
                'previous_time': existing_record.scan_time.strftime('%H:%M:%S')
            })
        
        # Create new attendance record
        attendance = AttendanceRecord(
            student_id=student.id,
            card_id=card_id,
            scan_datetime=scan_datetime,
            scan_date=scan_date,
            scan_time=scan_time,
            location=location,
            scanner_id=scanner_id,
            status='present'
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        logging.info(f"Attendance recorded for {student.name} ({student.roll_number}) at {scan_time}")
        
        return jsonify({
            'success': True,
            'message': 'Attendance recorded successfully',
            'student_name': student.name,
            'roll_number': student.roll_number,
            'scan_time': scan_time.strftime('%H:%M:%S')
        })
        
    except Exception as e:
        logging.error(f"Biometric scan error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to record attendance'})

@app.route('/api/attendance/filter', methods=['POST'])
def filter_attendance():
    """Filter attendance records based on session, campus, and course"""
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'})
        
        data = request.get_json()
        session_filter = data.get('session', '').strip()
        campus_filter = data.get('campus', '').strip()
        course_filter = data.get('course', '').strip()
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        # Build query
        query = db.session.query(AttendanceRecord, Student).join(Student)
        
        # Apply filters
        if session_filter:
            query = query.filter(Student.session == session_filter)
        if campus_filter:
            query = query.filter(Student.campus == campus_filter)
        if course_filter:
            query = query.filter(Student.course == course_filter)
        if date_from:
            query = query.filter(AttendanceRecord.scan_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(AttendanceRecord.scan_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        # Execute query
        results = query.order_by(AttendanceRecord.scan_datetime.desc()).all()
        
        # Format results
        attendance_data = []
        for attendance, student in results:
            attendance_data.append({
                'id': attendance.id,
                'name': student.name,
                'roll_number': student.roll_number,
                'session': student.session,
                'campus': student.campus,
                'course': student.course,
                'scan_date': attendance.scan_date.strftime('%Y-%m-%d'),
                'scan_time': attendance.scan_time.strftime('%H:%M:%S'),
                'location': attendance.location,
                'status': attendance.status
            })
        
        return jsonify({
            'success': True,
            'data': attendance_data,
            'count': len(attendance_data)
        })
        
    except Exception as e:
        logging.error(f"Filter attendance error: {e}")
        return jsonify({'success': False, 'message': 'Failed to filter attendance data'})

@app.route('/api/attendance/download', methods=['POST'])
def download_attendance():
    """Generate and download Excel report of filtered attendance data"""
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'})
        
        data = request.get_json()
        session_filter = data.get('session', '').strip()
        campus_filter = data.get('campus', '').strip()
        course_filter = data.get('course', '').strip()
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        # Build query (same as filter)
        query = db.session.query(AttendanceRecord, Student).join(Student)
        
        if session_filter:
            query = query.filter(Student.session == session_filter)
        if campus_filter:
            query = query.filter(Student.campus == campus_filter)
        if course_filter:
            query = query.filter(Student.course == course_filter)
        if date_from:
            query = query.filter(AttendanceRecord.scan_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(AttendanceRecord.scan_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        results = query.order_by(AttendanceRecord.scan_datetime.desc()).all()
        
        if not results:
            return jsonify({'success': False, 'message': 'No data found for the specified criteria'})
        
        # Generate Excel file
        excel_file = generate_excel_report(results, {
            'session': session_filter,
            'campus': campus_filter,
            'course': course_filter,
            'date_from': date_from,
            'date_to': date_to
        })
        
        # Create response
        response = make_response(excel_file.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return response
        
    except Exception as e:
        logging.error(f"Download attendance error: {e}")
        return jsonify({'success': False, 'message': 'Failed to generate report'})

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students for management"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'})
        
        students = Student.query.filter_by(is_active=True).order_by(Student.name).all()
        
        student_data = []
        for student in students:
            student_data.append({
                'id': student.id,
                'name': student.name,
                'roll_number': student.roll_number,
                'card_id': student.card_id,
                'session': student.session,
                'campus': student.campus,
                'course': student.course,
                'year': student.year
            })
        
        return jsonify({'success': True, 'data': student_data})
        
    except Exception as e:
        logging.error(f"Get students error: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch students'})

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'})
        
        today = date.today()
        
        # Total students
        total_students = Student.query.filter_by(is_active=True).count()
        
        # Today's attendance
        today_attendance = AttendanceRecord.query.filter_by(scan_date=today).count()
        
        # Attendance percentage
        attendance_percentage = (today_attendance / total_students * 100) if total_students > 0 else 0
        
        # Recent attendance (last 10 records)
        recent_attendance = db.session.query(AttendanceRecord, Student)\
            .join(Student)\
            .order_by(AttendanceRecord.scan_datetime.desc())\
            .limit(10).all()
        
        recent_data = []
        for attendance, student in recent_attendance:
            recent_data.append({
                'name': student.name,
                'roll_number': student.roll_number,
                'scan_time': attendance.scan_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'location': attendance.location
            })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_students': total_students,
                'today_attendance': today_attendance,
                'attendance_percentage': round(attendance_percentage, 1),
                'recent_attendance': recent_data
            }
        })
        
    except Exception as e:
        logging.error(f"Dashboard stats error: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch dashboard stats'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'message': 'Internal server error'}), 500
