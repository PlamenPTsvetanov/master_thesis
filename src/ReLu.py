# Apply ReLU to feature extraction
numbers = []
binary_numbers = [1 if num > 0.5 else 0 for num in numbers]

for num in binary_numbers:
    print(num)
