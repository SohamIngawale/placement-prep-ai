import json
import random
import uuid

# Define All Companies in the platform
COMPANIES = [
    'Accenture', 'Adobe', 'Amazon', 'Apple', 'Atlassian', 'Barclays', 'Capgemini', 'Cisco', 'Cognizant', 
    'Cred', 'DE Shaw', 'Deloitte', 'Deutsche Bank', 'EY', 'Flipkart', 'Freshworks', 'Goldman Sachs', 
    'Google', 'HCL Technologies', 'Hexaware', 'IBM', 'Infosys', 'Intel', 'JP Morgan', 'KPMG', 
    'LTIMindtree', 'Meta', 'Microsoft', 'Mindtree', 'Morgan Stanley', 'Mphasis', 'Myntra', 'Oracle', 
    'PayPal', 'Paytm', 'Persistent', 'PhonePe', 'Qualcomm', 'Razorpay', 'SAP', 'Salesforce', 'Samsung', 
    'Sprinklr', 'Swiggy', 'TCS', 'Tech Mahindra', 'Tower Research', 'Uber', 'VMware', 'Virtusa', 
    'Walmart', 'Wipro', 'Zoho', 'Zomato'
]

# Categorize companies for accurate question mapping
CATEGORIES = {
    "product": ['Adobe', 'Amazon', 'Apple', 'Atlassian', 'Cisco', 'Google', 'IBM', 'Intel', 'Meta', 'Microsoft', 'Oracle', 'PayPal', 'Qualcomm', 'SAP', 'Salesforce', 'Samsung', 'Uber', 'VMware', 'Walmart'],
    "service": ['Accenture', 'Capgemini', 'Cognizant', 'HCL Technologies', 'Hexaware', 'Infosys', 'LTIMindtree', 'Mindtree', 'Mphasis', 'Persistent', 'TCS', 'Tech Mahindra', 'Virtusa', 'Wipro'],
    "finance": ['Barclays', 'DE Shaw', 'Deutsche Bank', 'Goldman Sachs', 'JP Morgan', 'Morgan Stanley', 'Tower Research'],
    "startup": ['Cred', 'Flipkart', 'Freshworks', 'Myntra', 'Paytm', 'PhonePe', 'Razorpay', 'Sprinklr', 'Swiggy', 'Zoho', 'Zomato'],
    "consulting": ['Deloitte', 'EY', 'KPMG']
}

# --- MASTER QUESTION ARCHETYPES ---
# These are real-world questions often asked in interviews.

ARCHETYPES = {
    "dsa": [
        {"title": "Reverse a Linked List", "diff": "Easy", "text": "Given the head of a singly linked list, reverse the list and return its head.", "hint": "Use three pointers: prev, curr, and nxt.", "solution": "def reverseList(head):\n    prev = None\n    curr = head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev"},
        {"title": "Detect Cycle in Linked List", "diff": "Medium", "text": "Given head, the head of a linked list, determine if the linked list has a cycle in it.", "hint": "Use Floyd's Cycle-Finding Algorithm (slow and fast pointers).", "solution": "def hasCycle(head):\n    slow, fast = head, head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n        if slow == fast:\n            return True\n    return False"},
        {"title": "Valid Parentheses", "diff": "Easy", "text": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.", "hint": "Use a stack to track open brackets.", "solution": "def isValid(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top: return False\n        else:\n            stack.append(char)\n    return not stack"},
        {"title": "Two Sum", "diff": "Easy", "text": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.", "hint": "Use a hash map to store seen values.", "solution": "def twoSum(nums, target):\n    prevMap = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in prevMap: return [prevMap[diff], i]\n        prevMap[n] = i"},
        {"title": "Merge Intervals", "diff": "Medium", "text": "Given an array of intervals, merge all overlapping intervals.", "hint": "Sort the intervals by start time first.", "solution": "def merge(intervals):\n    intervals.sort(key=lambda i: i[0])\n    output = [intervals[0]]\n    for start, end in intervals[1:]:\n        lastEnd = output[-1][1]\n        if start <= lastEnd: output[-1][1] = max(lastEnd, end)\n        else: output.append([start, end])\n    return output"},
    ],
    "technical": [
        {"title": "OOPs: Polymorphism", "diff": "Easy", "text": "Explain Polymorphism with a real-world coding example.", "hint": "Mention method overloading and overriding.", "solution": "Polymorphism means 'many forms'. In OOP, it allows a single interface to represent different underlying forms. Example: Run-time polymorphism (Method Overriding) where a subclass provides a specific implementation of a method defined in its superclass."},
        {"title": "DBMS: ACID Properties", "diff": "Medium", "text": "What are ACID properties in a database? Explain each briefly.", "hint": "Atomicity, Consistency, Isolation, Durability.", "solution": "1. Atomicity: Transaction is all or nothing. 2. Consistency: Database remains valid after transaction. 3. Isolation: Transactions don't interfere. 4. Durability: Results are permanent after commit."},
        {"title": "OS: Deadlocks", "diff": "Medium", "text": "What is a Deadlock? What are the four necessary conditions for it?", "hint": "Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.", "solution": "Deadlock is a state where a set of processes are blocked because each process is holding a resource and waiting for another resource held by another process. Conditions: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait."},
        {"title": "Networking: TCP vs UDP", "diff": "Easy", "text": "Compare TCP and UDP protocols. Which is faster and why?", "hint": "TCP is connection-oriented (reliable), UDP is connectionless (fast).", "solution": "TCP is connection-oriented, ensuring reliable data delivery with error checking (slower). UDP is connectionless, sending data without verifying delivery (faster, used for streaming/gaming)."},
        {"title": "System Design: Load Balancers", "diff": "Medium", "text": "What is a Load Balancer? How does it help in scaling applications?", "hint": "Distributes incoming traffic across multiple servers.", "solution": "A Load Balancer acts as a reverse proxy that distributes network or application traffic across a number of servers. It improves application availability and reliability by preventing any single server from becoming a bottleneck."},
    ],
    "aptitude": [
        {"title": "Time & Work", "diff": "Medium", "text": "A can do a piece of work in 10 days and B can do it in 15 days. If they work together, how many days will they take?", "options": ["6 days", "5 days", "7 days", "8 days"], "answer": 0, "hint": "Work = 1/10 + 1/15 per day.", "solution": "Net work per day = 1/10 + 1/15 = 5/30 = 1/6. So they take 6 days total."},
        {"title": "Profit & Loss", "diff": "Easy", "text": "A shopkeeper sells a book for $240 and gains 20%. What is the cost price?", "options": ["$200", "$180", "$210", "$220"], "answer": 0, "hint": "CP = SP / (1 + Profit%).", "solution": "CP = 240 / (1 + 0.2) = 240 / 1.2 = 200."},
    ],
    "hr": [
        {"title": "Self Introduction", "diff": "Easy", "text": "Tell me about yourself and your background.", "hint": "Focus on education, projects, and skills.", "solution": "I am a [Your Degree] student at [Your University]. I am passionate about [Topic]. I have worked on [Project A] and [Project B], and I am looking for a role where I can contribute my skills in [Skill X]."},
        {"title": "Strengths & Weaknesses", "diff": "Easy", "text": "What are your greatest strengths and weaknesses?", "hint": "Be honest but professional; mention how you're improving your weakness.", "solution": "My strength is [Strength, e.g., quick learning]. My weakness is [Minor weakness, e.g., public speaking], but I am working on it by [Action, e.g., joining a debate club]."},
    ]
}

def generate_database():
    new_questions = []
    for company in COMPANIES:
        company_cat = "service"
        for cat, names in CATEGORIES.items():
            if company in names: company_cat = cat; break
        
        counts = {"aptitude": random.randint(3, 5), "hr": random.randint(2, 3), "dsa": random.randint(3, 5), "technical": random.randint(3, 5)}
        if company_cat in ["product", "finance", "startup"]:
            counts["dsa"] += 3; counts["technical"] += 2
        elif company_cat == "service":
            counts["aptitude"] += 3; counts["hr"] += 2
            
        for q_cat, count in counts.items():
            available = ARCHETYPES[q_cat]
            selected = random.sample(available, min(count, len(available)))
            for arch in selected:
                q_id = f"{q_cat[:3]}_{company.lower()[:3]}_{uuid.uuid4().hex[:6]}"
                q_obj = {
                    "id": q_id, "title": arch['title'], "company": company, "category": q_cat,
                    "difficulty": arch['diff'], "question": arch['text'], "hint": arch['hint'],
                    "solution": arch['solution'],
                }
                if q_cat == "aptitude":
                    q_obj["options"] = arch['options']; q_obj["answer"] = arch['answer']
                if q_cat == "dsa":
                    q_obj["code_template"] = "# Write your solution here\n"
                new_questions.append(q_obj)

    with open('data/questions.json', 'w', encoding='utf-8') as f:
        json.dump(new_questions, f, indent=2)
    return len(new_questions)

if __name__ == "__main__":
    count = generate_database()
    print(f"Successfully populated database for ALL {len(COMPANIES)} companies with REAL answers!")
    print(f"Total questions generated: {count}")
