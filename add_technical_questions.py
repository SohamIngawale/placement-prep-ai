import json
import uuid

tech_qs = [
    {
        "title": "OOP: Encapsulation vs Abstraction",
        "category": "technical",
        "difficulty": "Easy",
        "question": "What is the difference between Encapsulation and Abstraction in Object-Oriented Programming?",
        "hint": "Think about 'hiding data' vs 'hiding complexity'.",
        "solution": "Encapsulation is about wrapping data and methods into a single unit and restricting access to data (data hiding). Abstraction is about showing only necessary details to the user and hiding the background implementation (hiding complexity)."
    },
    {
        "title": "DBMS: Normalization",
        "category": "technical",
        "difficulty": "Medium",
        "question": "Explain the first three normal forms (1NF, 2NF, 3NF) in database design.",
        "hint": "Think about atomic values, partial dependencies, and transitive dependencies.",
        "solution": "1NF: Atomic values only. 2NF: 1NF + no partial functional dependency. 3NF: 2NF + no transitive functional dependency."
    },
    {
        "title": "OS: Virtual Memory",
        "category": "technical",
        "difficulty": "Medium",
        "question": "What is Virtual Memory? How does paging work?",
        "hint": "Think about how OS allows running programs larger than physical RAM.",
        "solution": "Virtual Memory is a memory management technique that provides an 'idealized' abstraction of the storage resources. Paging is a scheme where the OS retrieves data from secondary storage in same-size blocks called pages."
    },
    {
        "title": "Networking: OSI Model Layers",
        "category": "technical",
        "difficulty": "Easy",
        "question": "List the 7 layers of the OSI model and their primary functions.",
        "hint": "Please Do Not Throw Sausage Pizza Away (Physical, Data Link, Network, Transport, Session, Presentation, Application).",
        "solution": "1. Physical (Bits) 2. Data Link (Frames) 3. Network (Packets/Routing) 4. Transport (End-to-end reliability) 5. Session (Dialog management) 6. Presentation (Encryption/Compression) 7. Application (Network services)."
    },
    {
        "title": "Web: HTTP vs HTTPS",
        "category": "technical",
        "difficulty": "Easy",
        "question": "What are the main differences between HTTP and HTTPS?",
        "hint": "Think about security and SSL/TLS.",
        "solution": "HTTP is unsecured, while HTTPS is secured. HTTPS uses SSL/TLS certificates to encrypt communication between the client and the server, protecting against eavesdropping."
    },
    {
        "title": "Java: Interface vs Abstract Class",
        "category": "technical",
        "difficulty": "Medium",
        "question": "When should you use an Interface versus an Abstract Class in Java?",
        "hint": "Think about 'is-a' vs 'can-do' relationships.",
        "solution": "Use Abstract Class for 'is-a' relationships where you want to share code among closely related classes. Use Interface for 'can-do' relationships to define a contract that unrelated classes can implement."
    },
    {
        "title": "Python: List vs Tuple",
        "category": "technical",
        "difficulty": "Easy",
        "question": "What is the primary difference between a list and a tuple in Python?",
        "hint": "Think about mutability.",
        "solution": "Lists are mutable (can be changed after creation), while tuples are immutable (cannot be changed after creation). Lists use [] and tuples use ()."
    },
    {
        "title": "System Design: Microservices vs Monolith",
        "category": "technical",
        "difficulty": "Hard",
        "question": "Compare Monolithic architecture with Microservices architecture. What are the trade-offs?",
        "hint": "Think about scalability, deployment, and complexity.",
        "solution": "Monolith: Single unit, easy to develop/test initially, but hard to scale and slow to deploy as it grows. Microservices: Decoupled services, independent scaling and deployment, but high operational complexity and network overhead."
    },
    {
        "title": "DBMS: SQL vs NoSQL",
        "category": "technical",
        "difficulty": "Medium",
        "question": "When would you choose a NoSQL database over a traditional SQL database?",
        "hint": "Think about schema flexibility and horizontal scaling.",
        "solution": "Choose NoSQL when you have unstructured data, need a flexible schema, or require massive horizontal scaling. Choose SQL for complex queries, ACID compliance, and structured data relationships."
    },
    {
        "title": "SDLC: Agile vs Waterfall",
        "category": "technical",
        "difficulty": "Easy",
        "question": "What is the key difference between the Waterfall and Agile development models?",
        "hint": "Think about linear vs iterative processes.",
        "solution": "Waterfall is a linear, sequential approach where each phase must be completed before the next starts. Agile is iterative and incremental, focusing on continuous feedback and rapid delivery."
    }
]

COMPANIES = ['TCS', 'Infosys', 'Accenture', 'Cognizant', 'Wipro', 'Capgemini', 'IBM', 'Tech Mahindra', 'HCL', 'Deloitte']

expanded_qs = []
for q in tech_qs:
    for c in COMPANIES:
        new_q = q.copy()
        new_q['id'] = f"tec_{c.lower()[:3]}_{uuid.uuid4().hex[:6]}"
        new_q['company'] = c
        expanded_qs.append(new_q)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data.extend(expanded_qs)

with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Added {len(expanded_qs)} new Technical questions across {len(COMPANIES)} companies.")
