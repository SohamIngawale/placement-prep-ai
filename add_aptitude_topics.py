import json

# Define new aptitude questions across different topics
new_qs = [
    # --- Time & Work ---
    {
        "id": "apt_tw1",
        "title": "Time & Work",
        "company": "TCS",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A can finish a work in 18 days and B can do the same work in 15 days. B worked for 10 days and left the job. In how many days can A alone finish the remaining work?",
        "options": ["5 days", "6 days", "8 days", "10 days"],
        "answer": 1,
        "hint": "Calculate B's 10 days work. The remaining work is done by A."
    },
    {
        "id": "apt_tw2",
        "title": "Time & Work",
        "company": "Infosys",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A and B undertake to do a piece of work for Rs 600. A alone can do it in 6 days while B alone can do it in 8 days. With the help of C, they finish it in 3 days. Find the share of C.",
        "options": ["Rs 75", "Rs 90", "Rs 100", "Rs 120"],
        "answer": 0,
        "hint": "Share of money is proportional to the work done by each person."
    },
    {
        "id": "apt_tw3",
        "title": "Time & Work",
        "company": "Accenture",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "If 15 men can reap a field in 28 days, in how many days will 10 men reap it?",
        "options": ["42 days", "35 days", "30 days", "40 days"],
        "answer": 0,
        "hint": "Use the formula: M1 * D1 = M2 * D2"
    },

    # --- Profit & Loss ---
    {
        "id": "apt_pl1",
        "title": "Profit & Loss",
        "company": "Cognizant",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A shopkeeper sells two articles at Rs 1000 each. On one he gains 10% and on the other he loses 10%. Find his overall profit or loss percentage.",
        "options": ["1% Profit", "1% Loss", "No profit no loss", "2% Loss"],
        "answer": 1,
        "hint": "When selling price is same, and profit% = loss%, there is always a loss of (x^2 / 100)%."
    },
    {
        "id": "apt_pl2",
        "title": "Profit & Loss",
        "company": "Wipro",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "Cost price of 20 articles is equal to the selling price of x articles. If the profit is 25%, find the value of x.",
        "options": ["15", "16", "18", "25"],
        "answer": 1,
        "hint": "Profit % = ((CP of 20 - CP of x) / CP of x) * 100"
    },

    # --- Speed & Distance ---
    {
        "id": "apt_sd1",
        "title": "Speed Distance Time",
        "company": "TCS",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A train 125 m long passes a man, running at 5 km/hr in the same direction in which the train is going, in 10 seconds. Find the speed of the train.",
        "options": ["45 km/hr", "50 km/hr", "54 km/hr", "55 km/hr"],
        "answer": 1,
        "hint": "Relative speed = Speed of train - Speed of man. Convert m/s to km/hr."
    },
    {
        "id": "apt_sd2",
        "title": "Speed Distance Time",
        "company": "Capgemini",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "Without stoppages, a train travels at an average speed of 60 km/hr. With stoppages, it covers the same distance at an average speed of 48 km/hr. How many minutes per hour does the train stop?",
        "options": ["10 min", "12 min", "15 min", "18 min"],
        "answer": 1,
        "hint": "Time lost per hour = (Difference in speed / Faster speed) * 60 minutes."
    },

    # --- Percentages ---
    {
        "id": "apt_pc1",
        "title": "Percentages",
        "company": "Deloitte",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "Two students appeared at an examination. One of them secured 9 marks more than the other and his marks was 56% of the sum of their marks. Find the marks obtained by them.",
        "options": ["39, 30", "41, 32", "42, 33", "43, 34"],
        "answer": 2,
        "hint": "Let the marks be x and (x+9). Then (x+9) = 56% of (x + x + 9)."
    },
    {
        "id": "apt_pc2",
        "title": "Percentages",
        "company": "IBM",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "The population of a town increased from 1,75,000 to 2,62,500 in a decade. Find the average percent increase of population per year.",
        "options": ["4.37%", "5%", "6%", "8.75%"],
        "answer": 1,
        "hint": "Find the total percentage increase over 10 years, then divide by 10."
    },

    # --- Ratio & Proportion ---
    {
        "id": "apt_rp1",
        "title": "Ratio & Proportion",
        "company": "Amazon",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "Salaries of Ravi and Sumit are in the ratio 2:3. If the salary of each is increased by Rs 4000, the new ratio becomes 40:57. Find Sumit's present salary.",
        "options": ["Rs 17000", "Rs 20000", "Rs 25500", "Rs 38000"],
        "answer": 3,
        "hint": "Let original salaries be 2x and 3x. Then (2x + 4000) / (3x + 4000) = 40 / 57."
    }
]

# Create duplicates across major service companies
COMPANIES = ['TCS', 'Infosys', 'Accenture', 'Cognizant', 'Wipro']

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

print(f"Added {len(expanded_qs)} new aptitude questions.")
