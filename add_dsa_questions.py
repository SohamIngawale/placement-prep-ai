import json
import uuid

dsa_qs = [
    {
        "title": "Two Sum",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution.",
        "hint": "Try using a hash map to store the value and its index as you iterate through the array.",
        "solution": "def twoSum(nums, target):\n    prevMap = {} # val : index\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in prevMap:\n            return [prevMap[diff], i]\n        prevMap[n] = i",
        "code_template": "def twoSum(nums, target):\n    # Write your code here\n    pass",
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."}
        ]
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "You are given an array prices where prices[i] is the price of a given stock on the ith day. You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.",
        "hint": "Keep track of the minimum price seen so far and calculate the profit if you sold today.",
        "solution": "def maxProfit(prices):\n    res = 0\n    lowest = prices[0]\n    for price in prices:\n        if price < lowest:\n            lowest = price\n        res = max(res, price - lowest)\n    return res",
        "code_template": "def maxProfit(prices):\n    # Write your code here\n    pass",
        "examples": [
            {"input": "prices = [7,1,5,3,6,4]", "output": "5", "explanation": "Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5."}
        ]
    },
    {
        "title": "Valid Anagram",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
        "hint": "An anagram uses the same characters the same number of times. Consider using a hash map or sorting.",
        "solution": "def isAnagram(s, t):\n    if len(s) != len(t): return False\n    countS, countT = {}, {}\n    for i in range(len(s)):\n        countS[s[i]] = 1 + countS.get(s[i], 0)\n        countT[t[i]] = 1 + countT.get(t[i], 0)\n    return countS == countT",
        "code_template": "def isAnagram(s, t):\n    # Write your code here\n    pass"
    },
    {
        "title": "Binary Search",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.",
        "hint": "Use two pointers, left and right, and check the middle element.",
        "solution": "def search(nums, target):\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        m = l + ((r - l) // 2)\n        if nums[m] > target:\n            r = m - 1\n        elif nums[m] < target:\n            l = m + 1\n        else:\n            return m\n    return -1",
        "code_template": "def search(nums, target):\n    # Write your code here\n    pass"
    },
    {
        "title": "Linked List Cycle",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "Given head, the head of a linked list, determine if the linked list has a cycle in it.",
        "hint": "Use two pointers moving at different speeds (slow and fast).",
        "solution": "def hasCycle(head):\n    slow, fast = head, head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n        if slow == fast:\n            return True\n    return False",
        "code_template": "def hasCycle(head):\n    # Write your code here\n    pass"
    },
    {
        "title": "Invert Binary Tree",
        "category": "dsa",
        "difficulty": "Easy",
        "question": "Given the root of a binary tree, invert the tree, and return its root.",
        "hint": "Swap the left and right children recursively.",
        "solution": "def invertTree(root):\n    if not root: return None\n    tmp = root.left\n    root.left = root.right\n    root.right = tmp\n    invertTree(root.left)\n    invertTree(root.right)\n    return root",
        "code_template": "def invertTree(root):\n    # Write your code here\n    pass"
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "category": "dsa",
        "difficulty": "Medium",
        "question": "Given a string s, find the length of the longest substring without repeating characters.",
        "hint": "Use a sliding window with a set to keep track of characters in the current window.",
        "solution": "def lengthOfLongestSubstring(s):\n    charSet = set()\n    l = 0\n    res = 0\n    for r in range(len(s)):\n        while s[r] in charSet:\n            charSet.remove(s[l])\n            l += 1\n        charSet.add(s[r])\n        res = max(res, r - l + 1)\n    return res",
        "code_template": "def lengthOfLongestSubstring(s):\n    # Write your code here\n    pass"
    },
    {
        "title": "Container With Most Water",
        "category": "dsa",
        "difficulty": "Medium",
        "question": "You are given an integer array height of length n. Find two lines that together with the x-axis form a container, such that the container contains the most water. Return the maximum amount of water a container can store.",
        "hint": "Use two pointers starting from the ends and move the pointer with the smaller height.",
        "solution": "def maxArea(height):\n    l, r = 0, len(height) - 1\n    res = 0\n    while l < r:\n        area = min(height[l], height[r]) * (r - l)\n        res = max(res, area)\n        if height[l] < height[r]:\n            l += 1\n        else:\n            r -= 1\n    return res",
        "code_template": "def maxArea(height):\n    # Write your code here\n    pass"
    },
    {
        "title": "3Sum",
        "category": "dsa",
        "difficulty": "Medium",
        "question": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.",
        "hint": "Sort the array and use a three-pointer approach (one fixed, two moving).",
        "solution": "def threeSum(nums):\n    res = []\n    nums.sort()\n    for i, a in enumerate(nums):\n        if i > 0 and a == nums[i - 1]: continue\n        l, r = i + 1, len(nums) - 1\n        while l < r:\n            threeSum = a + nums[l] + nums[r]\n            if threeSum > 0: r -= 1\n            elif threeSum < 0: l += 1\n            else:\n                res.append([a, nums[l], nums[r]])\n                l += 1\n                while nums[l] == nums[l - 1] and l < r: l += 1\n    return res",
        "code_template": "def threeSum(nums):\n    # Write your code here\n    pass"
    },
    {
        "title": "Level Order Traversal",
        "category": "dsa",
        "difficulty": "Medium",
        "question": "Given the root of a binary tree, return the level order traversal of its nodes' values. (i.e., from left to right, level by level).",
        "hint": "Use a queue for Breadth-First Search (BFS).",
        "solution": "import collections\ndef levelOrder(root):\n    res = []\n    q = collections.deque([root])\n    while q:\n        level = []\n        for i in range(len(q)):\n            node = q.popleft()\n            if node:\n                level.append(node.val)\n                q.append(node.left)\n                q.append(node.right)\n        if level: res.append(level)\n    return res",
        "code_template": "def levelOrder(root):\n    # Write your code here\n    pass"
    }
]

COMPANIES = ['Google', 'Amazon', 'Microsoft', 'Meta', 'Netflix', 'Uber', 'Apple', 'Adobe', 'Oracle', 'Salesforce']

expanded_qs = []
for q in dsa_qs:
    # Add to multiple companies
    for c in COMPANIES:
        new_q = q.copy()
        new_q['id'] = f"dsa_{c.lower()[:3]}_{uuid.uuid4().hex[:6]}"
        new_q['company'] = c
        expanded_qs.append(new_q)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data.extend(expanded_qs)

with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Added {len(expanded_qs)} new DSA questions across {len(COMPANIES)} companies.")
