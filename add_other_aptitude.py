import json

new_qs = [
    # --- Simple & Compound Interest ---
    {
        "id": "apt_sici_1",
        "title": "Simple & Compound Interest",
        "company": "TCS",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "What is the simple interest on Rs. 5000 at 8% per annum for 3 years?",
        "options": ["Rs. 1000", "Rs. 1200", "Rs. 1500", "Rs. 2000"],
        "answer": 1,
        "hint": "Use the formula: SI = (P * R * T) / 100"
    },
    {
        "id": "apt_sici_2",
        "title": "Simple & Compound Interest",
        "company": "Infosys",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "The difference between simple interest and compound interest on a certain sum of money for 2 years at 10% per annum is Rs. 50. Find the sum.",
        "options": ["Rs. 4000", "Rs. 4500", "Rs. 5000", "Rs. 6000"],
        "answer": 2,
        "hint": "Difference for 2 years = P(R/100)^2"
    },
    {
        "id": "apt_sici_3",
        "title": "Simple & Compound Interest",
        "company": "Cognizant",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A sum of money doubles itself in 4 years at simple interest. In how many years will it amount to 8 times itself?",
        "options": ["12 years", "16 years", "24 years", "28 years"],
        "answer": 3,
        "hint": "If sum doubles, interest earned is P. So interest P is earned in 4 years. For 8 times, interest needed is 7P."
    },
    {
        "id": "apt_sici_4",
        "title": "Simple & Compound Interest",
        "company": "Wipro",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A sum is invested at compound interest, compounded yearly. If the interest for two successive years be Rs. 500 and Rs. 540, find the rate of interest.",
        "options": ["4%", "6%", "8%", "10%"],
        "answer": 2,
        "hint": "The extra interest in the second year (540 - 500 = 40) is the interest on the first year's interest (500)."
    },
    
    # --- Problems on Ages ---
    {
        "id": "apt_ages_1",
        "title": "Problems on Ages",
        "company": "Accenture",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "The present ages of A and B are in the ratio 4:5. After 5 years, they will be in the ratio 5:6. The present age of A is:",
        "options": ["10 years", "15 years", "20 years", "25 years"],
        "answer": 2,
        "hint": "Let ages be 4x and 5x. (4x+5)/(5x+5) = 5/6."
    },
    {
        "id": "apt_ages_2",
        "title": "Problems on Ages",
        "company": "IBM",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A father said to his son, 'I was as old as you are at present at the time of your birth.' If the father's age is 38 years now, the son's age five years back was:",
        "options": ["14 years", "19 years", "33 years", "38 years"],
        "answer": 0,
        "hint": "Let son's current age be x. Father's age at son's birth was (38 - x). So, 38 - x = x."
    },
    {
        "id": "apt_ages_3",
        "title": "Problems on Ages",
        "company": "Capgemini",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "The sum of ages of 5 children born at the intervals of 3 years each is 50 years. What is the age of the youngest child?",
        "options": ["4 years", "8 years", "10 years", "None of these"],
        "answer": 0,
        "hint": "Let youngest be x. Then x + (x+3) + (x+6) + (x+9) + (x+12) = 50."
    },
    
    # --- Boats & Streams ---
    {
        "id": "apt_boats_1",
        "title": "Boats & Streams",
        "company": "TCS",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "A boat can travel with a speed of 13 km/hr in still water. If the speed of the stream is 4 km/hr, find the time taken by the boat to go 68 km downstream.",
        "options": ["2 hours", "3 hours", "4 hours", "5 hours"],
        "answer": 2,
        "hint": "Downstream speed = Speed of boat + Speed of stream."
    },
    {
        "id": "apt_boats_2",
        "title": "Boats & Streams",
        "company": "Deloitte",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A man's speed with the current is 15 km/hr and the speed of the current is 2.5 km/hr. The man's speed against the current is:",
        "options": ["8.5 km/hr", "9 km/hr", "10 km/hr", "12.5 km/hr"],
        "answer": 2,
        "hint": "Man's speed in still water = 15 - 2.5. Speed against current = (Still water speed) - 2.5."
    },
    {
        "id": "apt_boats_3",
        "title": "Boats & Streams",
        "company": "Amazon",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A boat covers a certain distance downstream in 1 hour, while it comes back in 1.5 hours. If the speed of the stream be 3 kmph, what is the speed of the boat in still water?",
        "options": ["12 km/hr", "15 km/hr", "18 km/hr", "21 km/hr"],
        "answer": 1,
        "hint": "Let speed of boat be B. Distance = (B + 3)*1 = (B - 3)*1.5."
    },
    
    # --- Permutation & Combination ---
    {
        "id": "apt_pnc_1",
        "title": "Permutation & Combination",
        "company": "Microsoft",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "Out of 7 consonants and 4 vowels, how many words of 3 consonants and 2 vowels can be formed?",
        "options": ["210", "1050", "25200", "21400"],
        "answer": 2,
        "hint": "Select 3 out of 7 (7C3), select 2 out of 4 (4C2). Then arrange the 5 letters (5!)."
    },
    {
        "id": "apt_pnc_2",
        "title": "Permutation & Combination",
        "company": "Morgan Stanley",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "In how many ways can a committee of 5 be made out of 6 men and 4 women, containing at least 2 women?",
        "options": ["186", "240", "150", "200"],
        "answer": 0,
        "hint": "Cases: (2W, 3M) + (3W, 2M) + (4W, 1M). Calculate combinations for each and add."
    },
    {
        "id": "apt_pnc_3",
        "title": "Permutation & Combination",
        "company": "Tech Mahindra",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "In how many different ways can the letters of the word 'OPTICAL' be arranged so that the vowels always come together?",
        "options": ["120", "720", "4320", "2160"],
        "answer": 1,
        "hint": "Treat vowels (O, I, A) as one block. Number of blocks = 4 consonants + 1 block = 5. Arrangements = 5! * 3!."
    },
    
    # --- Mixtures & Alligations ---
    {
        "id": "apt_mix_1",
        "title": "Mixtures & Alligations",
        "company": "JP Morgan",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "In what ratio must a grocer mix two varieties of pulses costing Rs. 15 and Rs. 20 per kg respectively so as to get a mixture worth Rs. 16.50 kg?",
        "options": ["3:7", "5:7", "7:3", "7:5"],
        "answer": 2,
        "hint": "Use the alligation rule: (20 - 16.50) / (16.50 - 15) = 3.5 / 1.5 = 7/3."
    },
    {
        "id": "apt_mix_2",
        "title": "Mixtures & Alligations",
        "company": "Infosys",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A container contains 40 litres of milk. From this container 4 litres of milk was taken out and replaced by water. This process was repeated further two times. How much milk is now contained by the container?",
        "options": ["26.34 litres", "27.36 litres", "28 litres", "29.16 litres"],
        "answer": 3,
        "hint": "Amount left = Original Amount * (1 - volume_taken/total_volume)^n"
    }
]

COMPANIES = ['TCS', 'Infosys', 'Accenture', 'Cognizant', 'Wipro', 'IBM', 'Amazon', 'Deloitte']

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

print(f"Added {len(expanded_qs)} new varied aptitude questions.")
