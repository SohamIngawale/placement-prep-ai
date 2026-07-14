from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
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

from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import anthropic

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_me_in_production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Flask-Mail Config
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# Flask-Limiter Config
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

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
    otp_last_sent = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')
    is_banned = db.Column(db.Boolean, default=False)

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
        cols = ["points", "current_streak", "max_streak", "last_activity_date", "otp", "otp_expiry", "is_admin", "role", "is_verified", "otp_last_sent", "is_banned"]
        for col in cols:
            try:
                if col == "last_activity_date":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} DATE"))
                elif col == "otp_expiry":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} DATETIME"))
                elif col == "otp":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} VARCHAR(6)"))
                elif col in ["is_verified", "is_banned"]:
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} BOOLEAN DEFAULT 0"))
                elif col == "otp_last_sent":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} DATETIME"))
                elif col == "is_admin":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} BOOLEAN DEFAULT 0"))
                elif col == "role":
                    db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} VARCHAR(20) DEFAULT 'user'"))
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

@app.route('/admin')
def admin_page():
    if 'user' not in session: 
        return render_template('index.html')
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin':
        return render_template('index.html')
    return render_template('admin.html')

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
def send_otp_email(to_email, otp, subject="Your OTP Code"):
    if not app.config.get('MAIL_USERNAME'):
        print(f"DEBUG: Mail not configured. OTP for {to_email} is {otp}")
        return True
    try:
        msg = Message(subject, sender=app.config.get('MAIL_USERNAME'), recipients=[to_email])
        msg.body = f"Your OTP is: {otp}\n\nThis OTP is valid for 10 minutes."
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already taken"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed = generate_password_hash(data['password'])
    user = User(username=data['username'], email=data['email'], password_hash=hashed, is_verified=False)
    
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    user.otp_last_sent = datetime.utcnow()
    
    db.session.add(user)
    db.session.commit()
    
    send_otp_email(user.email, otp, "Verify your PlacePrep account")
    
    return jsonify({
        "message": "Registration successful. Please verify your email.",
        "username": user.username,
        "requires_verification": True
    })

@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    if getattr(user, 'is_banned', False):
        return jsonify({"error": "Your account has been banned."}), 403

    if not user.is_verified:
        return jsonify({"error": "Please verify your email first", "requires_verification": True}), 403

    session.permanent = True
    session['user'] = user.username
    return jsonify({
        "username": user.username,
        "points": user.points,
        "is_admin": user.role == 'admin'
    })

@app.route('/api/verify-email', methods=['POST'])
@limiter.limit("5 per minute")
def verify_email():
    data = request.json
    username = data.get('username')
    otp = data.get('otp')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200
        
    if user.otp != otp:
        return jsonify({"error": "Invalid OTP"}), 400
        
    if user.otp_expiry and user.otp_expiry < datetime.utcnow():
        return jsonify({"error": "OTP expired"}), 400
        
    user.is_verified = True
    user.otp = None
    user.otp_expiry = None
    db.session.commit()
    
    session.permanent = True
    session['user'] = user.username
    
    return jsonify({
        "message": "Email verified successfully",
        "username": user.username,
        "points": user.points,
        "is_admin": user.role == 'admin'
    })

@app.route('/api/resend-otp', methods=['POST'])
@limiter.limit("3 per minute")
def resend_otp():
    data = request.json
    username = data.get('username')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if user.is_verified:
        return jsonify({"error": "Email already verified"}), 400
        
    if user.otp_last_sent and (datetime.utcnow() - user.otp_last_sent).total_seconds() < 60:
        return jsonify({"error": "Please wait before requesting another OTP"}), 429
        
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    user.otp_last_sent = datetime.utcnow()
    db.session.commit()
    
    send_otp_email(user.email, otp, "Verify your PlacePrep account (Resend)")
    return jsonify({"message": "OTP sent to your email"})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/api/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"error": "No account found with this email"}), 404
    
    if user.otp_last_sent and (datetime.utcnow() - user.otp_last_sent).total_seconds() < 60:
        return jsonify({"error": "Please wait before requesting another OTP"}), 429

    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    user.otp_last_sent = datetime.utcnow()
    db.session.commit()
    
    send_otp_email(user.email, otp, "Password Reset OTP")
    return jsonify({"message": "OTP sent to your email", "username": user.username})

@app.route('/api/reset-password', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password():
    data = request.json
    username = data.get('username')
    otp = data.get('otp')
    new_password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or user.otp != otp:
        return jsonify({"error": "Invalid OTP"}), 400
    
    if user.otp_expiry and user.otp_expiry < datetime.utcnow():
        return jsonify({"error": "OTP expired"}), 400
    
    hashed = generate_password_hash(new_password)
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
        "points": user.points if user else 0,
        "is_admin": (user.role == 'admin') if user else False
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
COMPANIES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'companies.json')

@app.route('/api/companies')
def companies():
    try:
        with open(COMPANIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        "version": "*",
        "files": [{"name": "main", "content": code}]
    }
    try:
        response = requests.post(piston_url, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        print(f"Piston Response: {res_data}") # Debug log
        return jsonify(res_data)
    except Exception as e:
        print(f"Piston Error: {str(e)}")
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
@app.route('/api/admin/dashboard_stats')
def admin_dashboard_stats():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin': return jsonify({"error": "Forbidden"}), 403

    total_users = User.query.count()
    total_interviews = InterviewExperience.query.count()
    total_progress = Progress.query.filter_by(completed=True).count()
    
    # recent users
    recent_users = User.query.order_by(User.joined.desc()).limit(5).all()
    recent_users_data = [{"id": u.id, "username": u.username, "points": u.points, "joined": u.joined.strftime('%Y-%m-%d')} for u in recent_users]

    # chart data (last 5 days)
    five_days_ago = datetime.utcnow() - timedelta(days=4)
    all_users = User.query.filter(User.joined >= five_days_ago).all()
    counts = {}
    for i in range(5):
        d = (datetime.utcnow() - timedelta(days=4-i)).strftime('%Y-%m-%d')
        counts[d] = 0
    for u in all_users:
        d = u.joined.strftime('%Y-%m-%d')
        if d in counts:
            counts[d] += 1
    chart_data = [{"date": k, "count": v} for k, v in counts.items()]

    return jsonify({
        "total_users": total_users,
        "total_questions": len(ALL_QUESTIONS),
        "total_interviews": total_interviews,
        "total_progress": total_progress,
        "recent_users": recent_users_data,
        "chart_data": chart_data
    })

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin': return jsonify({"error": "Forbidden"}), 403

    users = User.query.order_by(User.joined.desc()).all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "points": u.points,
        "role": u.role,
        "joined": u.joined.strftime('%Y-%m-%d')
    } for u in users])

@app.route('/api/admin/users/<int:user_id>', methods=['PUT', 'DELETE'])
def admin_manage_user(user_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    admin_user = User.query.filter_by(username=session['user']).first()
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Forbidden"}), 403

    target_user = User.query.get(user_id)
    if not target_user: return jsonify({"error": "User not found"}), 404
    
    if target_user.id == admin_user.id:
        return jsonify({"error": "Cannot modify your own account"}), 400

    if request.method == 'DELETE':
        db.session.delete(target_user)
        db.session.commit()
        return jsonify({"success": True})
        
    if request.method == 'PUT':
        data = request.json
        if 'role' in data:
            target_user.role = data['role']
        if 'points' in data:
            target_user.points = int(data['points'])
        if 'is_banned' in data:
            target_user.is_banned = bool(data['is_banned'])
        if 'is_verified' in data:
            target_user.is_verified = bool(data['is_verified'])
        db.session.commit()
        return jsonify({"success": True})

@app.route('/api/admin/add_question', methods=['POST'])
def add_question():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin': return jsonify({"error": "Forbidden"}), 403

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

@app.route('/api/admin/companies', methods=['POST', 'PUT', 'DELETE'])
def admin_companies():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin': return jsonify({"error": "Forbidden"}), 403

    try:
        with open(COMPANIES_FILE, 'r', encoding='utf-8') as f:
            comps = json.load(f)
            
        data = request.json
        cat = data.get('category')
        
        if request.method == 'POST':
            if cat not in comps:
                comps[cat] = []
            comps[cat].append(data.get('company'))
        elif request.method == 'PUT':
            idx = data.get('index')
            if cat in comps and 0 <= idx < len(comps[cat]):
                comps[cat][idx] = data.get('company')
        elif request.method == 'DELETE':
            idx = data.get('index')
            if cat in comps and 0 <= idx < len(comps[cat]):
                comps[cat].pop(idx)
                
        with open(COMPANIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(comps, f, indent=4)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/interviews', methods=['GET', 'DELETE'])
def admin_interviews():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin': return jsonify({"error": "Forbidden"}), 403

    if request.method == 'DELETE':
        exp_id = request.args.get('id')
        exp = InterviewExperience.query.get(exp_id)
        if exp:
            db.session.delete(exp)
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"error": "Not found"}), 404

    exps = InterviewExperience.query.order_by(InterviewExperience.date_added.desc()).all()
    return jsonify([{
        "id": e.id,
        "username": e.username,
        "company": e.company,
        "role": e.role,
        "content": e.content,
        "date": e.date_added.strftime('%Y-%m-%d'),
        "difficulty": e.difficulty
    } for e in exps])

@app.route('/api/admin/questions/<q_id>', methods=['DELETE', 'PUT'])
def admin_manage_question(q_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin': return jsonify({"error": "Forbidden"}), 403

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            
        q_idx = next((i for i, q in enumerate(questions) if q['id'] == q_id), -1)
        if q_idx == -1: return jsonify({"error": "Question not found"}), 404
        
        if request.method == 'DELETE':
            deleted_q = questions.pop(q_idx)
            ALL_QUESTIONS[:] = [q for q in ALL_QUESTIONS if q['id'] != q_id]
            if deleted_q.get('category') in QUESTIONS:
                QUESTIONS[deleted_q['category']] = [q for q in QUESTIONS[deleted_q['category']] if q['id'] != q_id]
                
        elif request.method == 'PUT':
            data = request.json
            for k, v in data.items():
                questions[q_idx][k] = v
            # Update memory
            for i, q in enumerate(ALL_QUESTIONS):
                if q['id'] == q_id:
                    ALL_QUESTIONS[i] = questions[q_idx]
                    break
            cat = questions[q_idx].get('category')
            if cat in QUESTIONS:
                for i, q in enumerate(QUESTIONS[cat]):
                    if q['id'] == q_id:
                        QUESTIONS[cat][i] = questions[q_idx]
                        break

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2)
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/activity')
def admin_activity():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(username=session['user']).first()
    if not user or user.role != 'admin': return jsonify({"error": "Forbidden"}), 403
    
    activities = Activity.query.order_by(Activity.activity_date.desc()).limit(100).all()
    result = []
    for a in activities:
        u = User.query.get(a.user_id)
        if u:
            result.append({
                "username": u.username,
                "date": a.activity_date.strftime('%Y-%m-%d'),
                "count": a.count
            })
    return jsonify(result)

# ───── ERROR HANDLERS ─────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)