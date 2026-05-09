# 🎯 PlacePrep — Placement Preparation Platform

A full-stack web application for placement preparation covering **Aptitude, DSA, Technical Interview, and HR** questions for companies like Google, Amazon, Microsoft, TCS, Infosys, and Wipro.

---

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install flask
```

### 2. Run the App
```bash
cd placement_prep
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
placement_prep/
├── app.py                  ← Flask backend (API + routing)
├── requirements.txt
├── templates/
│   └── index.html          ← Single-page HTML frontend
└── static/
    ├── css/
    │   └── style.css       ← All styling
    └── js/
        └── app.js          ← Frontend logic & API calls
```

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Auth | Register / Login / Logout with session management |
| 📊 Dashboard | Track completed questions, bookmarks, scores |
| 🧮 Aptitude | MCQ questions with auto-grading & explanations |
| ⚡ DSA/Coding | Code templates, hints, and solution reveal |
| 💻 Technical | CS fundamentals (OOP, DBMS, OS, Networks) |
| 🤝 HR | Tips, sample answers, STAR method guidance |
| 🏢 Companies | Filter by Google, Amazon, Microsoft, TCS, Infosys, Wipro |
| 📌 Bookmarks | Save questions for later review |
| 🏆 Progress | Per-category progress bars |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register` | Create account |
| POST | `/api/login` | Login |
| POST | `/api/logout` | Logout |
| GET | `/api/me` | Current user info |
| GET | `/api/questions/<category>` | Get questions (aptitude/dsa/technical/hr) |
| GET | `/api/companies` | Get company data |
| GET | `/api/stats` | Platform statistics |
| POST | `/api/progress/complete` | Mark question complete |
| POST | `/api/progress/bookmark` | Toggle bookmark |
| GET | `/api/progress/me` | My progress |

---

## 🛠 Extending the App

### Add More Questions
Edit the `QUESTIONS` dictionary in `app.py`:
```python
QUESTIONS["aptitude"].append({
    "id": "apt6",
    "title": "New Question",
    "difficulty": "Medium",
    "company": ["TCS", "Google"],
    "question": "Your question text here",
    "options": ["A", "B", "C", "D"],
    "answer": 0,  # index of correct answer
    "explanation": "Why this is correct"
})
```

### Connect a Real Database
Replace the in-memory `USERS` and `PROGRESS` dicts with SQLite/PostgreSQL using Flask-SQLAlchemy.

---

## 📌 Tech Stack
- **Backend:** Python + Flask
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Fonts:** Syne (display) + DM Sans (body) + JetBrains Mono (code)
- **Auth:** Flask sessions + SHA-256 password hashing
