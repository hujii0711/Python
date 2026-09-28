"""
중첩 컬렉션
"""

# list of dict
users: list[dict[str, int]] = [
    {"age": 30},
    {"age": 25},
]

# dict of list
schedule: dict[str, list[str]] = {
    "mon": ["meeting", "lunch"],
    "tue": ["coding"],
}
