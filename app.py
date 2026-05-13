from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import io
import requests
import json
import os
import random
from datetime import datetime, date, timedelta
try:
    import PyPDF2
    import docx
except ImportError:
    pass

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import anthropic

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_me_in_production')

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# ───── DB CONFIG ─────
# Ensure instance folder exists
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

# Support for PostgreSQL (Heroku/Render) or SQLite (Local)
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    # Use absolute path for SQLite to avoid "unable to open database file" errors
    db_path = os.path.join(app.instance_path, 'placement.db')
    database_url = f'sqlite:///{db_path}'

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ───── MODELS ─────
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    points = db.Column(db.Integer, default=0)
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    current_streak = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    activity_date = db.Column(db.Date, default=date.today)
    count = db.Column(db.Integer, default=0)

class InterviewExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    company = db.Column(db.String(100))
    role = db.Column(db.String(100))
    content = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    difficulty = db.Column(db.String(20))

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    question_id = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)
    bookmarked = db.Column(db.Boolean, default=False)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    data = db.Column(db.Text) # JSON string

with app.app_context():
    db.create_all()
    # Safe migration: Add columns if they don't exist
    try:
        from sqlalchemy import text
        # Ignore errors if columns already exist
        cols = ["points", "current_streak", "max_streak", "last_activity_date", "otp", "otp_expiry"]
        for col in cols:
            try:
                if col == "last_activity_date":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} DATE"))
                elif col == "otp_expiry":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} DATETIME"))
                elif col == "otp":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} VARCHAR(6)"))
                else:
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} INTEGER DEFAULT 0"))
                db.session.commit()
            except Exception:
                db.session.rollback()
    except Exception:
        pass

# ───── HOME ─────
@app.route('/')
def home():
    return render_template('index.html')

# ───── LOAD QUESTIONS FROM JSON ─────
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    ALL_QUESTIONS = json.load(f)

# Group by category for quick access
QUESTIONS = {}
for q in ALL_QUESTIONS:
    cat = q.get('category', 'other')
    QUESTIONS.setdefault(cat, []).append(q)

print(f"Loaded {len(ALL_QUESTIONS)} questions across {list(QUESTIONS.keys())}")

# ───── AUTH ─────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User exists"}), 400

    hashed = hashlib.sha256(data['password'].encode()).hexdigest()
    user = User(username=data['username'], email=data['email'], password_hash=hashed)
    db.session.add(user)
    db.session.commit()
    session['user'] = user.username
    return jsonify({"username": user.username})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    hashed = hashlib.sha256(data['password'].encode()).hexdigest()
    user = User.query.filter_by(username=data['username']).first()

    if not user or user.password_hash != hashed:
        return jsonify({"error": "Invalid credentials"}), 401

    session['user'] = user.username
    return jsonify({"username": user.username})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # For security, don't reveal if user exists, but here we'll be helpful
        return jsonify({"error": "No account found with this email"}), 404
    
    # Generate 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    
    # SIMULATION: In a real app, send email. Here, we just return it or log it.
    print(f"DEBUG: Password reset OTP for {user.username} ({user.email}): {otp}")
    return jsonify({"message": "OTP sent to your email (Simulated)", "username": user.username})

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get('username')
    otp = data.get('otp')
    new_password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or user.otp != otp:
        return jsonify({"error": "Invalid OTP"}), 400
    
    if user.otp_expiry < datetime.utcnow():
        return jsonify({"error": "OTP expired"}), 400
    
    # Reset password
    hashed = hashlib.sha256(new_password.encode()).hexdigest()
    user.password_hash = hashed
    user.otp = None
    user.otp_expiry = None
    db.session.commit()
    
    return jsonify({"message": "Password updated successfully"})

@app.route('/api/me')
def me():
    if 'user' not in session:
        return jsonify({"logged_in": False})
    user = User.query.filter_by(username=session['user']).first()
    return jsonify({
        "logged_in": True, 
        "username": session['user'],
        "points": user.points if user else 0
    })

# ───── QUESTIONS ─────
@app.route('/api/questions/<category>')
def get_questions(category):
    qs = QUESTIONS.get(category, [])
    company = request.args.get('company')
    if company:
        qs = [q for q in qs if q.get('company', '').lower() == company.lower()]
    return jsonify({"questions": qs})

# ───── PROGRESS ─────
@app.route('/api/progress/complete', methods=['POST'])
def complete():
    if 'user' not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.json
    qid = data['qid']
    p = Progress.query.filter_by(username=session['user'], question_id=qid).first()
    
    # Check if newly completed to award points
    is_new = not p or not p.completed
    
    if not p:
        p = Progress(username=session['user'], question_id=qid)
    
    p.completed = True
    db.session.add(p)
    
    # Award points & update activity
    if is_new:
        user = User.query.filter_by(username=session['user']).first()
        if user:
            # Find difficulty
            q_diff = next((q.get('difficulty', 'Easy') for q in ALL_QUESTIONS if q['id'] == qid), 'Easy')
            points = 30 if q_diff == 'Hard' else (20 if 'Medium' in q_diff else 10)
            user.points = (user.points or 0) + points
            
            # Update Activity & Streak
            today = date.today()
            activity = Activity.query.filter_by(user_id=user.id, activity_date=today).first()
            if not activity:
                activity = Activity(user_id=user.id, activity_date=today, count=1)
                
                # Update Streak
                if user.last_activity_date:
                    if user.last_activity_date == today - timedelta(days=1):
                        user.current_streak += 1
                    elif user.last_activity_date < today - timedelta(days=1):
                        user.current_streak = 1
                else:
                    user.current_streak = 1
                
                user.max_streak = max(user.max_streak or 0, user.current_streak)
                user.last_activity_date = today
                db.session.add(activity)
            else:
                activity.count += 1
            
            db.session.add(user)
            
    db.session.commit()
    return jsonify({"message": "completed"})

@app.route('/api/leaderboard')
def leaderboard():
    users = User.query.order_by(User.points.desc().nulls_last()).limit(10).all()
    return jsonify({
        "leaderboard": [{"username": u.username, "points": u.points or 0} for u in users]
    })

@app.route('/api/progress/me')
def my_progress():
    if 'user' not in session:
        return jsonify({"completed": [], "bookmarks": []})

    progress = Progress.query.filter_by(username=session['user']).all()
    return jsonify({
        "completed": [p.question_id for p in progress if p.completed],
        "bookmarks": [p.question_id for p in progress if p.bookmarked]
    })

# ───── STATS ─────
@app.route('/api/stats')
def stats():
    total_users = User.query.count()
    total_questions = len(ALL_QUESTIONS)
    all_companies = set(q.get('company','') for q in ALL_QUESTIONS)
    return jsonify({
        "total_users": total_users,
        "total_questions": total_questions,
        "companies": len(all_companies)
    })

# ───── COMPANIES ─────
@app.route('/api/companies')
def companies():
    return jsonify({
        "product_mncs": [
            {"name": "Google", "logo": "G", "color": "#4285F4", "difficulty": "Hard", "rounds": "DSA + System Design + Technical", "categories": ["dsa", "technical"], "ctc": "25-45 LPA", "roles": "Software Engineer, SRE"},
            {"name": "Amazon", "logo": "A", "color": "#FF9900", "difficulty": "Medium-Hard", "rounds": "DSA + System Design + HR", "categories": ["dsa", "technical", "hr"], "ctc": "20-40 LPA", "roles": "SDE-1, Cloud Support"},
            {"name": "Microsoft", "logo": "M", "color": "#00A4EF", "difficulty": "Hard", "rounds": "DSA + System Design + Technical", "categories": ["dsa", "technical"], "ctc": "22-42 LPA", "roles": "Software Engineer"},
            {"name": "Meta", "logo": "F", "color": "#0668E1", "difficulty": "Hard", "rounds": "DSA + System Design + Behavioral", "categories": ["dsa", "technical"], "ctc": "30-50 LPA", "roles": "Front-End, Back-End"},
            {"name": "Apple", "logo": "🍎", "color": "#555555", "difficulty": "Hard", "rounds": "DSA + System Design + Domain", "categories": ["dsa", "technical"], "ctc": "25-45 LPA", "roles": "Hardware Engineer, SWE"},
            {"name": "Adobe", "logo": "Ad", "color": "#FF0000", "difficulty": "Medium-Hard", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "18-35 LPA", "roles": "MTS, Data Scientist"},
            {"name": "Oracle", "logo": "O", "color": "#F80000", "difficulty": "Medium", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "15-28 LPA", "roles": "Server Technology, Applications"},
            {"name": "Salesforce", "logo": "Sf", "color": "#00A1E0", "difficulty": "Medium-Hard", "rounds": "DSA + System Design + HR", "categories": ["dsa", "technical", "hr"], "ctc": "20-35 LPA", "roles": "AMTS"},
            {"name": "SAP", "logo": "S", "color": "#0FAAFF", "difficulty": "Medium", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "14-22 LPA", "roles": "Developer Associate"},
            {"name": "Cisco", "logo": "Ci", "color": "#049FD9", "difficulty": "Medium", "rounds": "DSA + Networking + HR", "categories": ["dsa", "technical", "hr"], "ctc": "15-25 LPA", "roles": "Network Engineer, SDE"},
            {"name": "Intel", "logo": "In", "color": "#0071C5", "difficulty": "Medium-Hard", "rounds": "DSA + Core CS + HR", "categories": ["dsa", "technical", "hr"], "ctc": "18-28 LPA", "roles": "System Software Engineer"},
            {"name": "Qualcomm", "logo": "Q", "color": "#3253DC", "difficulty": "Medium-Hard", "rounds": "DSA + Embedded + Technical", "categories": ["dsa", "technical"], "ctc": "16-30 LPA", "roles": "Hardware/Software Engineer"},
            {"name": "Samsung", "logo": "S", "color": "#1428A0", "difficulty": "Medium-Hard", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "14-20 LPA", "roles": "R&D Engineer"},
            {"name": "VMware", "logo": "V", "color": "#607078", "difficulty": "Medium-Hard", "rounds": "DSA + System Design + HR", "categories": ["dsa", "technical", "hr"], "ctc": "18-32 LPA", "roles": "MTS"},
            {"name": "PayPal", "logo": "PP", "color": "#003087", "difficulty": "Medium", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "20-30 LPA", "roles": "SDE-1"},
            {"name": "Uber", "logo": "U", "color": "#000000", "difficulty": "Hard", "rounds": "DSA + System Design + Behavioral", "categories": ["dsa", "technical"], "ctc": "30-55 LPA", "roles": "Software Engineer-1"},
            {"name": "Atlassian", "logo": "At", "color": "#0052CC", "difficulty": "Hard", "rounds": "DSA + System Design + Values", "categories": ["dsa", "technical"], "ctc": "28-48 LPA", "roles": "SDE"}
        ],
        "startups_unicorns": [
            {"name": "Flipkart", "logo": "F", "color": "#F7D03F", "difficulty": "Medium-Hard", "rounds": "DSA + Machine Coding + HR", "categories": ["dsa", "technical", "hr"], "ctc": "18-32 LPA", "roles": "SDE-1"},
            {"name": "Walmart", "logo": "W", "color": "#0071DC", "difficulty": "Medium-Hard", "rounds": "DSA + System Design + HR", "categories": ["dsa", "technical", "hr"], "ctc": "18-28 LPA", "roles": "SWE"},
            {"name": "Zoho", "logo": "Z", "color": "#C8202B", "difficulty": "Medium", "rounds": "Programming + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "8-14 LPA", "roles": "MTS"},
            {"name": "Razorpay", "logo": "R", "color": "#0C2651", "difficulty": "Medium-Hard", "rounds": "DSA + System Design + Culture", "categories": ["dsa", "technical"], "ctc": "20-35 LPA", "roles": "SDE-1"},
            {"name": "PhonePe", "logo": "Ph", "color": "#5F259F", "difficulty": "Medium", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "18-30 LPA", "roles": "SDE"},
            {"name": "Swiggy", "logo": "Sw", "color": "#FC8019", "difficulty": "Medium", "rounds": "DSA + Machine Coding + HR", "categories": ["dsa", "technical", "hr"], "ctc": "20-35 LPA", "roles": "SDE"},
            {"name": "Paytm", "logo": "P", "color": "#00BAF2", "difficulty": "Medium", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "12-20 LPA", "roles": "SDE"},
            {"name": "Freshworks", "logo": "Fw", "color": "#F36C21", "difficulty": "Medium", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "10-18 LPA", "roles": "Software Engineer"},
            {"name": "Sprinklr", "logo": "Sp", "color": "#1B365D", "difficulty": "Medium-Hard", "rounds": "DSA + System Design + HR", "categories": ["dsa", "technical", "hr"], "ctc": "22-38 LPA", "roles": "Product Engineer"},
            {"name": "Cred", "logo": "C", "color": "#2D2D2D", "difficulty": "Hard", "rounds": "DSA + System Design + Culture", "categories": ["dsa", "technical"], "ctc": "25-45 LPA", "roles": "Backend Engineer"},
            {"name": "Myntra", "logo": "M", "color": "#FF3F6C", "difficulty": "Medium", "rounds": "DSA + Machine Coding + HR", "categories": ["dsa", "technical", "hr"], "ctc": "15-28 LPA", "roles": "SDE"},
            {"name": "Zomato", "logo": "Z", "color": "#E23744", "difficulty": "Medium", "rounds": "DSA + Technical + HR", "categories": ["dsa", "technical", "hr"], "ctc": "18-30 LPA", "roles": "SDE"}
        ],
        "finance_consulting": [
            {"name": "Goldman Sachs", "logo": "GS", "color": "#6B9BC3", "difficulty": "Hard", "rounds": "DSA + Quant + Technical", "categories": ["dsa", "aptitude", "technical"], "ctc": "22-35 LPA", "roles": "Technology Analyst"},
            {"name": "Morgan Stanley", "logo": "MS", "color": "#002B5C", "difficulty": "Hard", "rounds": "DSA + Quant + Technical", "categories": ["dsa", "aptitude", "technical"], "ctc": "18-30 LPA", "roles": "Technology Analyst"},
            {"name": "JP Morgan", "logo": "JP", "color": "#003B6F", "difficulty": "Medium-Hard", "rounds": "DSA + Aptitude + Technical", "categories": ["dsa", "aptitude", "technical"], "ctc": "15-22 LPA", "roles": "Software Engineer"},
            {"name": "Deutsche Bank", "logo": "DB", "color": "#0018A8", "difficulty": "Medium-Hard", "rounds": "DSA + Aptitude + HR", "categories": ["dsa", "aptitude", "hr"], "ctc": "12-18 LPA", "roles": "Technology Graduate"},
            {"name": "Barclays", "logo": "B", "color": "#00AEEF", "difficulty": "Medium", "rounds": "DSA + Aptitude + HR", "categories": ["dsa", "aptitude", "hr"], "ctc": "12-16 LPA", "roles": "BA3 Developer"},
            {"name": "DE Shaw", "logo": "DE", "color": "#00263A", "difficulty": "Hard", "rounds": "DSA + Quant + System Design", "categories": ["dsa", "aptitude", "technical"], "ctc": "30-45 LPA", "roles": "MTS"},
            {"name": "Tower Research", "logo": "TR", "color": "#1C1C1C", "difficulty": "Hard", "rounds": "DSA + Quant + Puzzle", "categories": ["dsa", "aptitude"], "ctc": "35-50 LPA", "roles": "Core Developer"},
            {"name": "Deloitte", "logo": "D", "color": "#86BC25", "difficulty": "Medium", "rounds": "Aptitude + Case Study + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "6-10 LPA", "roles": "Analyst"},
            {"name": "EY", "logo": "EY", "color": "#FFE600", "difficulty": "Medium", "rounds": "Aptitude + GD + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "5-8 LPA", "roles": "Consultant"},
            {"name": "KPMG", "logo": "K", "color": "#00338D", "difficulty": "Medium", "rounds": "Aptitude + Case Study + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "5-8 LPA", "roles": "Analyst"}
        ],
        "service_companies": [
            {"name": "TCS", "logo": "T", "color": "#EE3A43", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "3.3 - 7.5 LPA", "roles": "Ninja, Digital"},
            {"name": "Infosys", "logo": "I", "color": "#007CC3", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "3.6 - 8 LPA", "roles": "System Engineer, SP"},
            {"name": "Wipro", "logo": "W", "color": "#6A1B9A", "difficulty": "Easy", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "3.5 - 6.5 LPA", "roles": "Project Engineer"},
            {"name": "Accenture", "logo": "A", "color": "#A100FF", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4.5 - 6.5 LPA", "roles": "ASE, FSE"},
            {"name": "Cognizant", "logo": "C", "color": "#1A4F8B", "difficulty": "Easy", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4 - 6.7 LPA", "roles": "GenC, GenC Elevate"},
            {"name": "HCL Technologies", "logo": "H", "color": "#0072C6", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "3.5 - 6 LPA", "roles": "Software Engineer"},
            {"name": "Tech Mahindra", "logo": "TM", "color": "#E31837", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "3.5 - 5.5 LPA", "roles": "Software Engineer"},
            {"name": "Capgemini", "logo": "Cg", "color": "#0070AD", "difficulty": "Easy-Medium", "rounds": "Aptitude + Pseudo Code + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4 - 7.5 LPA", "roles": "Analyst, Senior Analyst"},
            {"name": "IBM", "logo": "IB", "color": "#0043CE", "difficulty": "Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4.2 - 7.5 LPA", "roles": "Associate System Engineer"},
            {"name": "LTIMindtree", "logo": "LT", "color": "#005BAC", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4 - 6.5 LPA", "roles": "Software Engineer"},
            {"name": "Mphasis", "logo": "Mp", "color": "#231F20", "difficulty": "Easy", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "3.5 - 5 LPA", "roles": "Software Engineer"},
            {"name": "Persistent", "logo": "P", "color": "#15489D", "difficulty": "Medium", "rounds": "Aptitude + Coding + HR", "categories": ["aptitude", "dsa", "hr"], "ctc": "4.7 - 8 LPA", "roles": "Software Engineer"},
            {"name": "Hexaware", "logo": "Hx", "color": "#0072BC", "difficulty": "Easy", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4 - 6 LPA", "roles": "Software Engineer"},
            {"name": "Virtusa", "logo": "V", "color": "#E1251B", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4 - 6.5 LPA", "roles": "Associate Engineer"},
            {"name": "Mindtree", "logo": "Mt", "color": "#F3BF1E", "difficulty": "Easy-Medium", "rounds": "Aptitude + Technical + HR", "categories": ["aptitude", "technical", "hr"], "ctc": "4 - 6 LPA", "roles": "Software Engineer"}
        ]
    })

# ───── PROBLEM OF THE DAY ─────
@app.route('/api/potd')
def potd():
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    seed = sum(ord(c) for c in date_str)
    random.seed(seed)
    candidates = [q for q in ALL_QUESTIONS if q.get('difficulty') in ['Medium', 'Hard', 'Medium-Hard']]
    if not candidates: candidates = ALL_QUESTIONS
    chosen = random.choice(candidates)
    random.seed()
    return jsonify(chosen)

# ───── AI ANALYZER ─────
@app.route('/api/ai-review', methods=['POST'])
def ai_review():
    if request.content_type and 'multipart/form-data' in request.content_type:
        text = request.form.get('text', '').lower()
        rtype = request.form.get('type', 'resume')
        file = request.files.get('file')
        if file and file.filename:
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            try:
                if file_ext == 'pdf':
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages: text += " " + (page.extract_text() or "").lower()
                elif file_ext in ['docx', 'doc']:
                    doc = docx.Document(file)
                    text += " " + " ".join([p.text for p in doc.paragraphs]).lower()
                else: text += " " + file.read().decode('utf-8', errors='ignore').lower()
            except: return jsonify({"score": 0, "feedback": "Failed to parse file."})
    else:
        data = request.json or {}
        text = data.get('text', '').lower()
        rtype = data.get('type', 'resume')
    
    if len(text) < 20: return jsonify({"score": 10, "feedback": "Input too short."})
    score = 50
    feedback_points = []
    if rtype == 'resume':
        keywords = ['python', 'java', 'c++', 'react', 'sql', 'aws', 'docker', 'machine learning', 'api', 'database']
        if len([k for k in keywords if k in text]) > 3: score += 20
        if len([v for v in ['developed', 'designed', 'led', 'managed'] if v in text]) > 2: score += 20
        if '%' in text or 'increased' in text: score += 10
    score = min(100, score)
    return jsonify({"score": score, "feedback": " ".join(feedback_points) if feedback_points else "Looks solid!"})

# ───── MOCK TEST ─────
@app.route('/api/mock-test')
def mock_test():
    apt_qs = QUESTIONS.get("aptitude", [])
    count = min(5, len(apt_qs))
    return jsonify(random.sample(apt_qs, count) if count > 0 else [])

# ───── CODE EXECUTION ─────
@app.route('/api/run-code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    lang = request.json.get('language', 'python')
    piston_url = "https://emkc.org/api/v2/piston/execute"
    piston_key = os.environ.get('PISTON_API_KEY')
    headers = {"Authorization": piston_key} if piston_key else {}
    
    payload = {
        "language": lang,
        "version": "3.10.0" if lang == 'python' else "*",
        "files": [{"name": "main", "content": code}]
    }
    try:
        response = requests.post(piston_url, json=payload, headers=headers, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ───── INTERVIEW EXPERIENCES ─────
@app.route('/api/interviews', methods=['GET', 'POST'])
def interviews():
    if request.method == 'POST':
        if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        exp = InterviewExperience(
            username=session['user'],
            company=data.get('company'),
            role=data.get('role'),
            content=data.get('content'),
            difficulty=data.get('difficulty', 'Medium')
        )
        db.session.add(exp)
        db.session.commit()
        return jsonify({"message": "Success"})
    
    exps = InterviewExperience.query.order_by(InterviewExperience.date_added.desc()).all()
    return jsonify({
        "experiences": [{
            "username": e.username,
            "company": e.company,
            "role": e.role,
            "content": e.content,
            "date": e.date_added.strftime('%b %d, %Y'),
            "difficulty": e.difficulty
        } for e in exps]
    })

# ───── ACTIVITY DATA ─────
@app.route('/api/activity')
def get_activity():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user: return jsonify({"error": "User not found"}), 404
    
    activities = Activity.query.filter_by(user_id=user.id).all()
    return jsonify({
        "streak": user.current_streak,
        "max_streak": user.max_streak,
        "activity": {a.activity_date.isoformat(): a.count for a in activities}
    })

# ───── RESUME BUILDER ─────
@app.route('/api/resume', methods=['GET', 'POST'])
def handle_resume():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    if request.method == 'POST':
        data = request.json
        resume = Resume.query.filter_by(username=session['user']).first()
        if not resume:
            resume = Resume(username=session['user'])
        resume.data = json.dumps(data)
        db.session.add(resume)
        db.session.commit()
        return jsonify({"message": "Saved successfully"})
    
    resume = Resume.query.filter_by(username=session['user']).first()
    return jsonify(json.loads(resume.data) if resume else {})

# ───── AI FEATURES ─────
@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    if not anthropic_client:
        return jsonify({"error": "Anthropic API key is not configured"}), 500
    
    data = request.json
    messages = data.get('messages', [])
    system_prompt = data.get('system_prompt', "You are a helpful assistant.")
    
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )
        return jsonify({"reply": response.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-roadmap', methods=['POST'])
def generate_roadmap():
    if not anthropic_client:
        return jsonify({"error": "Anthropic API key is not configured"}), 500
    
    data = request.json
    company = data.get('company', 'Any Company')
    role = data.get('role', 'Software Engineer')
    skills = data.get('skills', 'Basics of Programming')
    duration = data.get('duration', '30') # days
    
    prompt = f"""
    Create a detailed {duration}-day placement preparation roadmap for a {role} position at {company}.
    The user's current skills: {skills}.
    
    Format the response as a JSON object with the following structure:
    {{
        "title": "Roadmap Title",
        "description": "Short overview",
        "phases": [
            {{
                "name": "Phase 1: Title",
                "days": "Day 1-10",
                "tasks": ["Task 1", "Task 2"],
                "resources": ["Topic 1", "Topic 2"]
            }}
        ],
        "tips": ["Tip 1", "Tip 2"]
    }}
    Return ONLY the JSON object.
    """
    
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            temperature=0.7,
            system="You are a senior placement coordinator and career coach. You provide highly structured, realistic, and effective study plans in JSON format.",
            messages=[{"role": "user", "content": prompt}]
        )
        # Parse JSON from response
        content = response.content[0].text
        # Find JSON block if Claude adds text
        if "{" in content:
            content = content[content.find("{"):content.rfind("}")+1]
        
        return jsonify(json.loads(content))
    except Exception as e:
        print(f"Error generating roadmap: {e}")
        return jsonify({"error": str(e)}), 500

# ───── ADMIN ─────
@app.route('/api/admin/add_question', methods=['POST'])
def add_question():
    data = request.json
    company = data.get('company')
    category = data.get('category', 'technical')
    difficulty = data.get('difficulty', 'Medium')
    question_text = data.get('question')
    solution = data.get('solution', '')

    if not company or not question_text:
        return jsonify({"success": False, "error": "Company and question are required"}), 400

    new_q = {
        "id": f"{category[:3]}_{random.randint(10000, 99999)}",
        "title": f"{company} Placement Question",
        "company": company,
        "category": category,
        "difficulty": difficulty,
        "question": question_text,
        "hint": "Try to think about the core concepts.",
        "solution": solution,
        "code_template": "# Type your solution here\n"
    }

    try:
        # Append to file
        with open(DATA_FILE, 'r+', encoding='utf-8') as f:
            questions = json.load(f)
            questions.append(new_q)
            f.seek(0)
            json.dump(questions, f, indent=2)
            f.truncate()

        # Update in-memory data
        ALL_QUESTIONS.append(new_q)
        QUESTIONS.setdefault(category, []).append(new_q)

        return jsonify({"success": True, "question": new_q})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ───── ERROR HANDLERS ─────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)