import json
import random

companies_dsa = ["Amazon", "Google", "Microsoft", "Meta"]
companies_service = ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant"]

dsa_topics = [
    "Two Sum", "Binary Search", "Sliding Window Maximum", "Longest Substring",
    "Merge Intervals", "LRU Cache", "Clone Graph", "Topological Sort",
    "Dijkstra", "Kadane Maximum Subarray", "Reverse Linked List",
    "Detect Cycle in Linked List", "Kth Largest Element", "Heap Merge K Lists",
    "Word Ladder", "Trie Implementation", "Union Find", "DP Coin Change",
    "DP LIS", "Matrix BFS"
]

apt_topics = [
    "Percentage", "Profit & Loss", "Time & Work", "Speed Distance Time",
    "Simple Interest", "Compound Interest", "Ratio & Proportion",
    "Number Series", "Pipes & Cistern", "Probability"
]

tech_topics = [
    "OOP Concepts", "Polymorphism", "Inheritance", "Encapsulation",
    "DBMS Normalization", "ACID Properties", "Indexing",
    "OS Deadlock", "Paging vs Segmentation", "TCP vs UDP",
    "REST API Design", "Load Balancer", "Caching", "CAP Theorem"
]

hr_topics = [
    "Tell me about yourself", "Strengths and Weaknesses",
    "Why this company?", "5-year plan", "Handling pressure",
    "Team conflict", "Leadership example"
]

def make_question(qid, title, category, company, difficulty):
    return {
        "id": qid,
        "title": title,
        "company": company,
        "category": category,
        "difficulty": difficulty,
        "question": f"{title} problem statement for {company}.",
        "hint": f"Key idea: {title}.",
        "solution": f"Approach for {title}.",
        "code_template": "# write code" if category == "dsa" else ""
    }

dataset = []
qid = 1

# 150 DSA
for _ in range(150):
    dataset.append(make_question(
        f"dsa{qid}",
        random.choice(dsa_topics),
        "dsa",
        random.choice(companies_dsa),
        random.choice(["Easy", "Medium", "Hard"])
    ))
    qid += 1

# 80 Aptitude
for _ in range(80):
    dataset.append(make_question(
        f"apt{qid}",
        random.choice(apt_topics),
        "aptitude",
        random.choice(companies_service),
        random.choice(["Easy", "Medium"])
    ))
    qid += 1

# 50 Technical
for _ in range(50):
    dataset.append(make_question(
        f"tech{qid}",
        random.choice(tech_topics),
        "technical",
        random.choice(companies_dsa),
        random.choice(["Easy", "Medium"])
    ))
    qid += 1

# 20 HR
for _ in range(20):
    dataset.append(make_question(
        f"hr{qid}",
        random.choice(hr_topics),
        "hr",
        random.choice(companies_service),
        "Easy"
    ))
    qid += 1

with open("data/questions.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("✅ Generated 300 questions in data/questions.json")