import json

new_qs = [
    {
        "id": "aptitude_hard1",
        "title": "Probability",
        "company": "Amazon",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A bag contains 5 red, 4 green, and 3 blue balls. If 3 balls are drawn at random without replacement, what is the probability that exactly 2 are red?",
        "options": ["12/55", "15/55", "10/55", "8/55"],
        "answer": 0,
        "hint": "Calculate ways to choose 2 red balls out of 5, and 1 non-red ball out of the remaining 7."
    },
    {
        "id": "aptitude_hard2",
        "title": "Permutations",
        "company": "Google",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "In how many ways can the letters of the word 'ENGINEERING' be arranged such that all the vowels are always together?",
        "options": ["1663200", "277200", "138600", "55440"],
        "answer": 1,
        "hint": "Treat all vowels (E, I, E, E, I) as a single block. Then arrange the block and the remaining consonants, taking duplicate letters into account."
    },
    {
        "id": "aptitude_hard3",
        "title": "Time & Work",
        "company": "Goldman Sachs",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A, B, and C can complete a piece of work in 10, 12, and 15 days respectively. They started the work together, but A left 2 days before the completion of the work and B left 3 days before the completion of the work. In how many days was the work completed?",
        "options": ["4.5 days", "5.8 days", "6.2 days", "7 days"],
        "answer": 1,
        "hint": "Assume the total work is completed in 'x' days. Formulate an equation based on their individual 1-day work rates."
    },
    {
        "id": "aptitude_hard4",
        "title": "Speed Distance Time",
        "company": "TCS",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "Two trains start at the same time from A and B and proceed toward each other at 45 km/hr and 60 km/hr respectively. When they meet, it is found that one train has traveled 120 km more than the other. Find the distance between A and B.",
        "options": ["720 km", "840 km", "960 km", "1080 km"],
        "answer": 1,
        "hint": "The difference in their speeds causes the difference in distance. The time traveled by both is the same."
    },
    {
        "id": "aptitude_hard5",
        "title": "Geometry",
        "company": "Infosys",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A cone, a hemisphere, and a cylinder stand on equal bases and have the same height. What is the ratio of their volumes?",
        "options": ["1:2:3", "2:1:3", "3:2:1", "1:3:2"],
        "answer": 0,
        "hint": "Use the formulas for the volume of a cone (1/3 πr²h), a hemisphere (2/3 πr³), and a cylinder (πr²h), noting that h = r."
    }
]

# Create duplicates across companies so it shows up globally
COMPANIES = ['Accenture', 'Microsoft', 'Capgemini', 'Wipro', 'Meta']

expanded_qs = []
for q in new_qs:
    expanded_qs.append(q)
    for idx, c in enumerate(COMPANIES):
        new_q = q.copy()
        new_q['id'] = q['id'] + "_" + str(idx)
        new_q['company'] = c
        expanded_qs.append(new_q)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data.extend(expanded_qs)

with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Added {len(expanded_qs)} hard aptitude questions.")
