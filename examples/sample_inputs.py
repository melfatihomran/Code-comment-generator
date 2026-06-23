"""
A few code snippets for manually testing the demo app / notebook baseline.
Paste any of the function bodies below into the UI at http://localhost:8000.
"""

EXAMPLES = [
    """def add(a, b):
    return a + b""",

    """def is_palindrome(s):
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]""",

    """def flatten(nested_list):
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result""",

    """def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1""",
]
