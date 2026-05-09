import json
with open('data/questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

categories = ['aptitude', 'dsa', 'technical', 'hr']
for cat in categories:
    unique_qs = set(q.get('question', '') for q in qs if q.get('category') == cat)
    print(f"Unique {cat} questions: {len(unique_qs)}")
    
    topics = {}
    for q in qs:
        if q.get('category') == cat:
            title = q.get('title', 'Unknown')
            topics[title] = topics.get(title, set())
            topics[title].add(q.get('question', ''))

    # print top 5 topics for each cat
    sorted_topics = sorted(topics.items(), key=lambda x: len(x[1]), reverse=True)
    for topic, unique_texts in sorted_topics[:5]:
        print(f"  - {topic}: {len(unique_texts)} unique questions")
    print("-" * 20)
