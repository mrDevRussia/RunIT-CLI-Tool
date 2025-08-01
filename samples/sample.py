// Sample JavaScript code for testing conversion
def calculateSum(numbers):
    sum = 0
    for (i = 0; i < numbers.__len__(); i += 1) :        sum += numbers[i]

    print(f"The sum is: ${sum}")
    return sum

    numbers = [1, 2, 3, 4, 5]
    result = calculateSum(numbers)
    print(f"Result: ${result}")