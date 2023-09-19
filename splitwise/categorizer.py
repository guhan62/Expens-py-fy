splitwise_id = {
    # Utilities
    "cleaning": 48,
    "electricity": 5,
    "heat/gas": 6,
    "other": 44,
    "utilities": 11,
    "trash": 37,
    "tv/phone/internet": 8,
    "water": 7,
    # Uncategorized
    "general": 18,
    # Entertainment
    "games": 20,
    "movies": 21,
    "music": 22,
    "entertainment": 23,
    "sports": 24,
    # Food And Drink
    "dining out": 13,
    "groceries": 12,
    "liquor": 38,
    "food and drink": 26,
    "electronics": 39,
    # Home
    "furniture": 16,
    "household supplies": 14,
    "maintenance": 17,
    "mortgage": 4,
    "home": 28,
    "pets": 29,
    "rent": 3,
    "services": 30,
    # Transportation
    "bicycle": 46,
    "bus/train": 32,
    "car": 15,
    "gas/fuel": 33,
    "hotel": 47,
    "transportation": 34,
    "parking": 9,
    "plane": 35,
    "taxi": 36,
    # Life
    "childcare": 50,
    "clothing": 41,
    "education": 49,
    "gifts": 42,
    "insurance": 10,
    "medical expenses": 43,
    "life": 44,
    "taxes": 45
}


# constants
BUCKET_2_SPLIT = {
    'education': splitwise_id["education"],
    'shopping': splitwise_id["life"],
    'entertainment': splitwise_id["entertainment"],
    'misc': splitwise_id["general"],
    'travel': splitwise_id["transportation"],
    'eshopping' : splitwise_id["life"],
    'market': splitwise_id["groceries"],
    'repayments': splitwise_id["life"],
    'fees': splitwise_id["life"],
    'games': splitwise_id["games"],
    'fuel': splitwise_id["gas/fuel"],
    'food': splitwise_id["dining out"],
    'refund': splitwise_id["life"],
    'internet': splitwise_id["tv/phone/internet"],
    'health': splitwise_id["medical expenses"],
    'personal': splitwise_id["life"],
    'auto': splitwise_id["car"],
    'insurance': splitwise_id["insurance"],
    'no-cat': splitwise_id["general"]
}