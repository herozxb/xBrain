# Python3 - Control Flow

## If-Elif-Else Statements
```python
# PROBLEM: Conditional execution in Python
# APPROACH: Use if-elif-else for branching logic
# TIME: O(1) SPACE: O(1)

score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

# Ternary operator
status = "pass" if score >= 60 else "fail"

# Multiple conditions
age, has_id = 20, True
can_enter = age >= 18 and has_id
```

**Explanation**: Python uses if-elif-else for conditional branching. Ternary operator provides concise conditionals.
---

## For Loops
```python
# PROBLEM: Iterating over sequences
# APPROACH: Use for loop with range, lists, or iterators
# TIME: O(n) SPACE: O(1)

# Range iteration
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

for i in range(2, 8):
    print(i)  # 2, 3, 4, 5, 6, 7

for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# List iteration
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Enumerate for index
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# Dictionary iteration
person = {"name": "Alice", "age": 30}
for key, value in person.items():
    print(f"{key}: {value}")
```

**Explanation**: for loops iterate over any iterable. Use enumerate() for index access.
---

## While Loops
```python
# PROBLEM: Looping until condition is false
# APPROACH: Use while loop with condition
# TIME: O(n) SPACE: O(1)

# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# While with else
num = 0
while num < 3:
    print(num)
    num += 1
else:
    print("Loop completed")

# Break and continue
i = 0
while True:
    i += 1
    if i == 3:
        continue  # Skip 3
    if i == 6:
        break     # Stop at 6
    print(i)

# Input validation loop
while True:
    value = input("Enter positive number: ")
    if value.isdigit() and int(value) > 0:
        break
```

**Explanation**: while loops continue until condition is False. Use break/continue for control.
---

## List Comprehensions
```python
# PROBLEM: Create lists concisely
# APPROACH: Use list comprehension syntax
# TIME: O(n) SPACE: O(n)

# Basic comprehension
squares = [x**2 for x in range(5)]
# [0, 1, 4, 9, 16]

# With condition
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]

# With transformation
words = ["hello", "world", "python"]
upper_words = [w.upper() for w in words]
# ["HELLO", "WORLD", "PYTHON"]

# Nested comprehension
matrix = [[i*j for j in range(3)] for i in range(3)]
# [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

# Flatten nested list
flat = [item for row in matrix for item in row]

# Dictionary comprehension
word_lengths = {w: len(w) for w in words}
# {"hello": 5, "world": 5, "python": 6}

# Set comprehension
unique_lengths = {len(w) for w in words}
# {5, 6}
```

**Explanation**: Comprehensions provide concise syntax for creating collections from iterables.
---

## Try-Except Error Handling
```python
# PROBLEM: Handle errors gracefully
# APPROACH: Use try-except blocks
# TIME: O(1) SPACE: O(1)

# Basic try-except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")

# Multiple exceptions
try:
    value = int("abc")
except (ValueError, TypeError) as e:
    print(f"Error: {e}")

# Try-except-else-finally
try:
    file = open("data.txt")
    content = file.read()
except FileNotFoundError:
    print("File not found")
else:
    print("File read successfully")
    print(content)
finally:
    print("Cleanup complete")

# Raising exceptions
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age

# Custom exception
class CustomError(Exception):
    pass

raise CustomError("Something went wrong")
```

**Explanation**: try-except handles exceptions. Use else for success code, finally for cleanup.
