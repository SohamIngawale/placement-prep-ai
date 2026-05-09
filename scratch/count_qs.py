import json
with open('data/questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)
unique_qs = set(q.get('question', '') for q in qs if q.get('category') == 'aptitude')
print(f"Unique aptitude questions: {len(unique_qs)}")
topics = {}
for q in qs:
    if q.get('category') == 'aptitude':
        title = q.get('title', 'Unknown')
        topics[title] = topics.get(title, set())
        topics[title].add(q.get('question', ''))

for topic, unique_texts in topics.items():
    print(f"  - {topic}: {len(unique_texts)} unique questions")
