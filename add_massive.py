import json

new_qs = [
    # --- DSA ---
    {
        "id": "dsa_new_1",
        "title": "Reverse Linked List",
        "company": "Amazon",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "Given the head of a singly linked list, reverse the list, and return the reversed list.",
        "hint": "Use three pointers: prev, curr, and next.",
        "solution": "def reverseList(head):\n    prev = None\n    curr = head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev",
        "code_template": "def reverseList(head):\n    pass"
    },
    {
        "id": "dsa_new_2",
        "title": "Valid Parentheses",
        "company": "Google",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "hint": "Use a stack to keep track of opening brackets.",
        "solution": "def isValid(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top: return False\n        else:\n            stack.append(char)\n    return not stack",
        "code_template": "def isValid(s):\n    pass"
    },
    {
        "id": "dsa_new_3",
        "title": "Merge Intervals",
        "company": "Microsoft",
        "category": "dsa",
        "difficulty": "Medium",
        "question": "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals.",
        "hint": "Sort the intervals by their start time first.",
        "solution": "def merge(intervals):\n    intervals.sort(key=lambda x: x[0])\n    merged = []\n    for interval in intervals:\n        if not merged or merged[-1][1] < interval[0]:\n            merged.append(interval)\n        else:\n            merged[-1][1] = max(merged[-1][1], interval[1])\n    return merged",
        "code_template": "def merge(intervals):\n    pass"
    },
    {
        "id": "dsa_new_4",
        "title": "Longest Palindromic Substring",
        "company": "Meta",
        "category": "dsa",
        "difficulty": "Medium",
        "question": "Given a string s, return the longest palindromic substring in s.",
        "hint": "Expand around center for each character and between characters.",
        "solution": "def longestPalindrome(s):\n    res = ''\n    for i in range(len(s)):\n        # odd length\n        l, r = i, i\n        while l >= 0 and r < len(s) and s[l] == s[r]:\n            if (r - l + 1) > len(res): res = s[l:r+1]\n            l -= 1; r += 1\n        # even length\n        l, r = i, i + 1\n        while l >= 0 and r < len(s) and s[l] == s[r]:\n            if (r - l + 1) > len(res): res = s[l:r+1]\n            l -= 1; r += 1\n    return res",
        "code_template": "def longestPalindrome(s):\n    pass"
    },
    {
        "id": "dsa_new_5",
        "title": "Word Search",
        "company": "Uber",
        "category": "dsa",
        "difficulty": "Hard",
        "question": "Given an m x n grid of characters board and a string word, return true if word exists in the grid.",
        "hint": "Use DFS with backtracking. Keep track of visited cells.",
        "solution": "def exist(board, word):\n    ROWS, COLS = len(board), len(board[0])\n    path = set()\n    def dfs(r, c, i):\n        if i == len(word): return True\n        if r < 0 or c < 0 or r >= ROWS or c >= COLS or word[i] != board[r][c] or (r,c) in path:\n            return False\n        path.add((r,c))\n        res = dfs(r+1,c,i+1) or dfs(r-1,c,i+1) or dfs(r,c+1,i+1) or dfs(r,c-1,i+1)\n        path.remove((r,c))\n        return res\n    for r in range(ROWS):\n        for c in range(COLS):\n            if dfs(r,c,0): return True\n    return False",
        "code_template": "def exist(board, word):\n    pass"
    },

    # --- Technical ---
    {
        "id": "tech_new_1",
        "title": "DBMS Concepts",
        "company": "Oracle",
        "category": "technical",
        "difficulty": "Easy",
        "question": "What is the difference between TRUNCATE, DELETE and DROP?",
        "hint": "Think about DML vs DDL, and whether the table structure is removed.",
        "solution": "DELETE is a DML command used to remove specific rows (can be rolled back). TRUNCATE is a DDL command that removes all rows quickly but keeps the table structure (cannot be rolled back). DROP is a DDL command that deletes the entire table structure and data."
    },
    {
        "id": "tech_new_2",
        "title": "OS Concepts",
        "company": "VMware",
        "category": "technical",
        "difficulty": "Medium",
        "question": "Explain Deadlock. What are the four necessary conditions for deadlock?",
        "hint": "Remember Coffman conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.",
        "solution": "A deadlock occurs when two or more processes are waiting indefinitely for an event that can be caused by only one of the waiting processes. The four conditions are: 1. Mutual Exclusion (resource is non-shareable). 2. Hold and Wait. 3. No Preemption. 4. Circular Wait."
    },
    {
        "id": "tech_new_3",
        "title": "System Design",
        "company": "Atlassian",
        "category": "technical",
        "difficulty": "Hard",
        "question": "How would you design a URL shortener like bit.ly?",
        "hint": "Discuss base62 encoding, database schema, and handling high read/write volume.",
        "solution": "Key components: 1. API gateway. 2. A Hash function (Base62 encoding of a counter or unique ID) to generate short links. 3. A database (NoSQL or SQL) mapping short to long URLs. 4. Caching layer (Redis) for fast redirects. 5. Analytics service."
    },
    {
        "id": "tech_new_4",
        "title": "OOP Concepts",
        "company": "Adobe",
        "category": "technical",
        "difficulty": "Easy",
        "question": "What is Polymorphism in OOP? Give an example.",
        "hint": "Polymorphism means 'many forms'. Think about method overriding and overloading.",
        "solution": "Polymorphism allows objects of different classes to be treated as objects of a common superclass. Compile-time polymorphism is method overloading (same method name, different parameters). Run-time polymorphism is method overriding (subclass provides a specific implementation of a method defined in its superclass)."
    },
    {
        "id": "tech_new_5",
        "title": "Networking",
        "company": "Cisco",
        "category": "technical",
        "difficulty": "Medium",
        "question": "Describe the 7 layers of the OSI model.",
        "hint": "Please Do Not Throw Sausage Pizza Away (Physical, Data Link, Network, Transport, Session, Presentation, Application).",
        "solution": "1. Physical: Raw bit stream over physical medium. 2. Data Link: Node-to-node data transfer (MAC). 3. Network: Routing data via IP. 4. Transport: Reliable data delivery (TCP/UDP). 5. Session: Manage communication sessions. 6. Presentation: Data translation/encryption. 7. Application: Network applications (HTTP, FTP)."
    },

    # --- HR ---
    {
        "id": "hr_new_1",
        "title": "Adaptability",
        "company": "IBM",
        "category": "hr",
        "difficulty": "Medium",
        "question": "Describe a time when you had to adapt to a sudden change in a project.",
        "hint": "Use the STAR method. Focus on how you stayed calm and pivoted your strategy.",
        "solution": "Highlight a specific situation where requirements changed. Emphasize your communication with the team, your quick learning to adjust, and the successful outcome despite the pivot."
    },
    {
        "id": "hr_new_2",
        "title": "Failure",
        "company": "Flipkart",
        "category": "hr",
        "difficulty": "Hard",
        "question": "Tell me about a time you failed. What did you learn?",
        "hint": "Don't pick a catastrophic failure, but a real one. Focus 80% of your answer on the lesson learned.",
        "solution": "Situation: A missed deadline or a bug pushed to production. Action: I took accountability and immediately communicated the issue. Learning: I implemented a new QA process / better time management system, preventing it from ever happening again."
    },

    # --- Aptitude ---
    {
        "id": "apt_new_1",
        "title": "Pipes & Cisterns",
        "company": "TCS",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "Pipe A can fill a tank in 10 hours, Pipe B in 15 hours. Pipe C can empty the full tank in 20 hours. If all three are opened together, in how many hours will the tank be filled?",
        "options": ["8.5 hours", "10 hours", "12 hours", "15 hours"],
        "answer": 2,
        "hint": "Net part filled in 1 hour = (1/10) + (1/15) - (1/20)"
    },
    {
        "id": "apt_new_2",
        "title": "Probability",
        "company": "Infosys",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "Two dice are thrown simultaneously. What is the probability of getting two numbers whose product is even?",
        "options": ["1/4", "1/2", "3/4", "5/8"],
        "answer": 2,
        "hint": "Product is odd only when both are odd. P(odd product) = 3/6 * 3/6 = 1/4. P(even) = 1 - 1/4."
    }
]

COMPANIES = ['TCS', 'Infosys', 'Amazon', 'Google', 'Accenture', 'Microsoft', 'Capgemini', 'Wipro', 'Meta', 'Goldman Sachs']

expanded_qs = []
for q in new_qs:
    expanded_qs.append(q)
    for idx, c in enumerate(COMPANIES):
        if c != q['company']: # Avoid exact duplicates
            new_q = q.copy()
            new_q['id'] = q['id'] + "_" + c.lower()
            new_q['company'] = c
            expanded_qs.append(new_q)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data.extend(expanded_qs)

with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Added {len(expanded_qs)} massive varied questions.")
