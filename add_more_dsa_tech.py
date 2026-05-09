import json
import uuid

# --- MORE DSA ---
more_dsa = [
    {"title": "Reverse String", "category": "dsa", "difficulty": "Easy", "question": "Write a function that reverses a string. The input string is given as an array of characters s.", "solution": "def reverseString(s):\n    l, r = 0, len(s) - 1\n    while l < r:\n        s[l], s[r] = s[r], s[l]\n        l, r = l + 1, r - 1"},
    {"title": "Valid Palindrome", "category": "dsa", "difficulty": "Easy", "question": "Given a string s, return true if it is a palindrome, or false otherwise.", "solution": "def isPalindrome(s):\n    l, r = 0, len(s) - 1\n    while l < r:\n        while l < r and not s[l].isalnum(): l += 1\n        while l < r and not s[r].isalnum(): r -= 1\n        if s[l].lower() != s[r].lower(): return False\n        l, r = l + 1, r - 1\n    return True"},
    {"title": "Climbing Stairs", "category": "dsa", "difficulty": "Easy", "question": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?", "solution": "def climbStairs(n):\n    one, two = 1, 1\n    for i in range(n - 1):\n        temp = one\n        one = one + two\n        two = temp\n    return one"},
    {"title": "Min Stack", "category": "dsa", "difficulty": "Medium", "question": "Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.", "solution": "class MinStack:\n    def __init__(self):\n        self.stack = []\n        self.minStack = []\n    def push(self, val):\n        self.stack.append(val)\n        val = min(val, self.minStack[-1] if self.minStack else val)\n        self.minStack.append(val)\n    def pop(self):\n        self.stack.pop()\n        self.minStack.pop()\n    def top(self):\n        return self.stack[-1]\n    def getMin(self):\n        return self.minStack[-1]"},
    {"title": "Number of Islands", "category": "dsa", "difficulty": "Medium", "question": "Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.", "solution": "def numIslands(grid):\n    if not grid: return 0\n    rows, cols = len(grid), len(grid[0])\n    visit = set()\n    islands = 0\n    def bfs(r, c):\n        q = collections.deque()\n        visit.add((r, c))\n        q.append((r, c))\n        while q:\n            row, col = q.popleft()\n            directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]\n            for dr, dc in directions:\n                r, c = row + dr, col + dc\n                if (r in range(rows) and c in range(cols) and grid[r][c] == '1' and (r, c) not in visit):\n                    q.append((r, c))\n                    visit.add((r, c))\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1' and (r, c) not in visit:\n                bfs(r, c)\n                islands += 1\n    return islands"}
]

# --- MORE TECHNICAL ---
more_tech = [
    {"title": "OS: Process vs Thread", "category": "technical", "difficulty": "Easy", "question": "What is the main difference between a Process and a Thread?", "solution": "A process is an independent program in execution with its own memory space. A thread is a subset of a process that shares the same memory space as other threads in the same process."},
    {"title": "DBMS: Primary Key vs Unique Key", "category": "technical", "difficulty": "Easy", "question": "Explain the difference between a Primary Key and a Unique Key.", "solution": "A Primary Key uniquely identifies each record and cannot be NULL. A Unique Key also ensures uniqueness but can accept one NULL value. A table can have only one Primary Key but multiple Unique Keys."},
    {"title": "C++: Pointers vs References", "category": "technical", "difficulty": "Medium", "question": "What is the difference between pointers and references in C++?", "solution": "Pointers can be re-assigned and can be NULL. References must be initialized when created and cannot be re-assigned or NULL."},
    {"title": "Java: HashMap vs HashTable", "category": "technical", "difficulty": "Medium", "question": "Compare HashMap and HashTable in Java.", "solution": "HashMap is non-synchronized and allows one NULL key. HashTable is synchronized (thread-safe) and does not allow NULL keys or values."},
    {"title": "System Design: CAP Theorem", "category": "technical", "difficulty": "Hard", "question": "What is the CAP Theorem in distributed systems?", "solution": "CAP stands for Consistency, Availability, and Partition Tolerance. The theorem states that a distributed system can only provide two out of these three guarantees simultaneously."}
]

COMPANIES = ['TCS', 'Infosys', 'Accenture', 'Cognizant', 'Wipro', 'Google', 'Amazon', 'Microsoft', 'Meta', 'Apple']

expanded_qs = []
for q in more_dsa + more_tech:
    for c in COMPANIES:
        new_q = q.copy()
        new_q['id'] = f"{q['category'][:3]}_{c.lower()[:3]}_{uuid.uuid4().hex[:6]}"
        new_q['company'] = c
        expanded_qs.append(new_q)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data.extend(expanded_qs)

with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Added {len(expanded_qs)} additional DSA & Technical questions.")
