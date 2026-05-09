import json

pl_qs = [
    {
        "id": "apt_pl_101",
        "title": "Profit & Loss",
        "company": "TCS",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "A person bought an article for Rs. 400 and sold it for Rs. 500. Find the profit percentage.",
        "options": ["20%", "25%", "30%", "35%"],
        "answer": 1,
        "hint": "Profit = SP - CP. Profit % = (Profit / CP) * 100"
    },
    {
        "id": "apt_pl_102",
        "title": "Profit & Loss",
        "company": "Infosys",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "If the cost price of 15 pens is equal to the selling price of 20 pens, find the loss percentage.",
        "options": ["15%", "20%", "25%", "33.33%"],
        "answer": 2,
        "hint": "Let CP of 1 pen = Rs 1. Then CP of 20 pens = Rs 20. SP of 20 pens = CP of 15 pens = Rs 15. Loss = Rs 5."
    },
    {
        "id": "apt_pl_103",
        "title": "Profit & Loss",
        "company": "Accenture",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A shopkeeper sells an article at a loss of 12.5%. Had he sold it for Rs. 51.80 more, he would have earned a profit of 6%. Find the cost price of the article.",
        "options": ["Rs. 280", "Rs. 300", "Rs. 380", "Rs. 400"],
        "answer": 0,
        "hint": "Let CP be x. SP1 = 0.875x. SP2 = 1.06x. Difference is 51.80."
    },
    {
        "id": "apt_pl_104",
        "title": "Profit & Loss",
        "company": "Wipro",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "A man sells two horses for Rs. 4000 each. On one he gains 10% and on the other he loses 10%. What is his overall gain or loss percentage?",
        "options": ["1% gain", "1% loss", "2% loss", "No profit no loss"],
        "answer": 1,
        "hint": "When two articles are sold at the same price, one at a gain of x% and other at a loss of x%, there is always an overall loss of (x/10)^2 %."
    },
    {
        "id": "apt_pl_105",
        "title": "Profit & Loss",
        "company": "Cognizant",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "By selling 45 lemons for Rs 40, a man loses 20%. How many should he sell for Rs 24 to gain 20% in the transaction?",
        "options": ["16", "18", "20", "22"],
        "answer": 1,
        "hint": "SP of 45 lemons = Rs 40. Loss = 20%, so CP of 45 lemons = Rs 50. For 20% gain, SP of 45 lemons = Rs 60."
    },
    {
        "id": "apt_pl_106",
        "title": "Profit & Loss",
        "company": "Capgemini",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A dishonest dealer professes to sell his goods at cost price, but he uses a weight of 900 grams for the kg weight. Find his gain percent.",
        "options": ["9%", "10%", "11.11%", "12.5%"],
        "answer": 2,
        "hint": "Gain % = (Error / (True Weight - Error)) * 100"
    },
    {
        "id": "apt_pl_107",
        "title": "Profit & Loss",
        "company": "Amazon",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A trader marks his goods at 20% above the cost price. He sells half the stock at the marked price, one quarter at a discount of 20% on the marked price, and the rest at a discount of 40% on the marked price. His total gain is:",
        "options": ["2%", "4.5%", "13.5%", "20%"],
        "answer": 0,
        "hint": "Assume CP = 100, MP = 120. Calculate total SP for 100 units of stock."
    },
    {
        "id": "apt_pl_108",
        "title": "Profit & Loss",
        "company": "Deloitte",
        "category": "aptitude",
        "difficulty": "Medium",
        "question": "The percentage profit earned by selling an article for Rs. 1920 is equal to the percentage loss incurred by selling the same article for Rs. 1280. At what price should the article be sold to make 25% profit?",
        "options": ["Rs. 1800", "Rs. 2000", "Rs. 2200", "Rs. 2400"],
        "answer": 1,
        "hint": "Since profit % = loss %, the CP is exactly in the middle of the two selling prices."
    },
    {
        "id": "apt_pl_109",
        "title": "Profit & Loss",
        "company": "Tech Mahindra",
        "category": "aptitude",
        "difficulty": "Hard",
        "question": "A manufacturer sells a pair of glasses to a wholesale dealer at a profit of 18%. The wholesaler sells the same to a retailer at a profit of 20%. The retailer in turn sells them to a customer for Rs. 30.09, thereby earning a profit of 25%. The cost price for the manufacturer is:",
        "options": ["Rs. 15", "Rs. 16", "Rs. 17", "Rs. 18"],
        "answer": 2,
        "hint": "Let original CP = x. Then x * 1.18 * 1.20 * 1.25 = 30.09."
    },
    {
        "id": "apt_pl_110",
        "title": "Profit & Loss",
        "company": "HCL Technologies",
        "category": "aptitude",
        "difficulty": "Easy",
        "question": "Some articles were bought at 6 articles for Rs. 5 and sold at 5 articles for Rs. 6. Gain percent is:",
        "options": ["30%", "33.33%", "35%", "44%"],
        "answer": 3,
        "hint": "Find the CP of 1 article and SP of 1 article. Or take LCM of 5 and 6."
    }
]

# Create duplicates across major service companies so they show globally
COMPANIES = ['TCS', 'Infosys', 'Accenture', 'Cognizant', 'Wipro', 'IBM']

expanded_qs = []
for q in pl_qs:
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

print(f"Added {len(expanded_qs)} new Profit & Loss questions.")
