numbers1 = []
numbers2 = []

missmatch = 0
for i in range(0, len(numbers1)):
    if numbers1[i] != numbers2[i]:
        missmatch += 1

print("{0:0.2f}".format(100 - (missmatch / len(numbers1)) * 100))

