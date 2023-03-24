class MyObject:
    def __init__(self, value):
        self.value = value
    
    def print_value(self):
        print(self.value)

# Create a 2D array of MyObject instances
my_array = [[MyObject(1), MyObject(2)], [MyObject(3), MyObject(4)]]

# Call a method on an object in the array
my_array[0][1].print_value()  # Output: 1