def sample_function():
    def example_function():
        # Function body goes here
        pass
        a = 10
        print(a)
    
    example_function()
    a = 10  # Assigning value to 'a' inside the scope of sample_function
    b = 20
    c = a + b
    print(c)

# Call the main function
sample_function()